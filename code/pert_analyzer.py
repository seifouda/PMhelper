#!/usr/bin/env python3
"""
PERT Analyzer Module

Handles probabilistic analysis for project management using Program Evaluation
and Review Technique (PERT). Works with optimistic, most likely, and pessimistic
time estimates.
"""

import numpy as np
import networkx as nx
from scipy.stats import norm
import math


class PERTAnalyzer:
    """PERT analysis functionality for probabilistic project management"""

    def __init__(self):
        self.G = None
        self.critical_paths = []
        self.critical_activities = []
        self.project_variance = 0
        self.project_std = 0

    def load_activities_from_pert_data(self, activities_data):
        """
        Load activities from PERT data format
        Expected data format: list of dicts with keys: id, predecessors, optimistic, most_likely, pessimistic
        """
        activities = []

        for row in activities_data:
            # Extract PERT time estimates
            try:
                optimistic = float(row['optimistic'])
                most_likely = float(row['most_likely'])
                pessimistic = float(row['pessimistic'])
            except (ValueError, KeyError) as e:
                raise ValueError(
                    f"Invalid PERT times for activity {
                        row.get(
                            'id', 'Unknown')}: {
                        str(e)}")

            # Calculate expected time and variance
            expected_time = (optimistic + 4 * most_likely + pessimistic) / 6
            variance = ((pessimistic - optimistic) / 6) ** 2

            # Round expected time up (ceil) and variance to 3 decimal places
            expected_time_ceil = math.ceil(expected_time)
            variance_rounded = round(variance, 3)

            # Process predecessors (comma-separated list)
            predecessors = []
            if row.get('predecessors') and str(row['predecessors']).strip():
                predecessors = [
                    p.strip() for p in str(
                        row['predecessors']).split(',') if p.strip()]

            # Get activity name (optional)
            activity_name = row.get('activity', '').strip()

            # Handle additional fields for full PERT support
            min_duration = int(
                row.get(
                    'min_duration',
                    1)) if row.get('min_duration') else 1
            crash_cost = int(
                row.get(
                    'crash_cost',
                    0)) if row.get('crash_cost') else 0
            resource_demand = int(
                row.get(
                    'resource_demand',
                    0)) if row.get('resource_demand') else 0
            normal_cost = int(
                row.get(
                    'normal_cost',
                    0)) if row.get('normal_cost') else 0

            activities.append({
                'id': row['id'],
                'activity': activity_name,
                'optimistic': optimistic,
                'most_likely': most_likely,
                'pessimistic': pessimistic,
                'expected_time': expected_time,
                'expected_time_ceil': expected_time_ceil,
                'variance': variance_rounded,
                'duration': expected_time_ceil,  # Use ceiling for all calculations
                'predecessors': predecessors,
                'min_duration': min_duration,
                'crash_cost': crash_cost,
                'resource_demand': resource_demand,
                'normal_cost': normal_cost
            })

        return activities

    def build_network(self, activities):
        """Build a directed graph network from PERT activity data"""
        # Create directed graph
        G = nx.DiGraph()

        # Add all activities as nodes with PERT attributes
        for activity in activities:
            G.add_node(
                activity['id'],
                duration=activity['duration'],  # Expected time (ceil)
                optimistic=activity['optimistic'],
                most_likely=activity['most_likely'],
                pessimistic=activity['pessimistic'],
                expected_time=activity['expected_time'],
                expected_time_ceil=activity['expected_time_ceil'],
                variance=activity['variance'],
                activity=activity.get('activity', ''),
                min_duration=activity.get('min_duration', 1),
                crash_cost=activity.get('crash_cost', 0),
                resource_demand=activity.get('resource_demand', 0),
                normal_cost=activity.get('normal_cost', 0)
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
            G.add_node(
                'START',
                duration=0,
                activity='Start',
                variance=0,
                optimistic=0,
                most_likely=0,
                pessimistic=0,
                expected_time=0,
                expected_time_ceil=0,
                min_duration=0,
                crash_cost=0,
                resource_demand=0,
                normal_cost=0)
            for node in start_nodes:
                G.add_edge('START', node)

        # Add END node and connect nodes with no successors to it
        end_nodes = [node for node in G.nodes() if G.out_degree(node)
                     == 0 and node != 'START']
        if end_nodes:
            G.add_node(
                'END',
                duration=0,
                activity='End',
                variance=0,
                optimistic=0,
                most_likely=0,
                pessimistic=0,
                expected_time=0,
                expected_time_ceil=0,
                min_duration=0,
                crash_cost=0,
                resource_demand=0,
                normal_cost=0)
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

    def calculate_project_variance(self, G, critical_path):
        """Calculate the total project variance based on critical path activities"""
        total_variance = 0
        if critical_path:
            for activity in critical_path:
                if activity in G.nodes and activity not in ['START', 'END']:
                    total_variance += G.nodes[activity]['variance']

        return round(total_variance, 3)

    def analyze(self, activities_data):
        """Perform complete PERT analysis"""
        activities = self.load_activities_from_pert_data(activities_data)
        self.G = self.build_network(activities)
        self.G = self.forward_pass(self.G)
        self.G = self.backward_pass(self.G)
        self.G = self.calculate_float(self.G)
        self.critical_paths, self.critical_activities = self.identify_critical_path(
            self.G)

        # Calculate project statistics
        if self.critical_paths and self.critical_paths[0]:
            self.project_variance = self.calculate_project_variance(
                self.G, self.critical_paths[0])
            self.project_std = round(np.sqrt(self.project_variance), 3)
        else:
            self.project_variance = 0
            self.project_std = 0

        return self.G, self.critical_paths, self.critical_activities

    def calculate_completion_probability(self, target_duration):
        """
        Calculate the probability of completing the project within target_duration
        """
        if not self.G:
            raise ValueError("No network graph available. Run analysis first.")

        # Get expected duration from critical path
        if self.critical_paths and self.critical_paths[0]:
            # Calculate expected duration from critical path expected times
            expected_duration = 0
            critical_path = self.critical_paths[0]

            for activity in critical_path:
                if activity in self.G.nodes and activity not in [
                        'START', 'END']:
                    expected_duration += self.G.nodes[activity]['expected_time']
        else:
            # Fallback to EF calculation if no critical path
            expected_duration = max([self.G.nodes[node]['EF']
                                    for node in self.G.nodes()])

        # Handle zero variance case
        if self.project_std == 0:
            return 1.0 if target_duration >= expected_duration else 0.0

        # Calculate Z-score
        z_score = (target_duration - expected_duration) / self.project_std

        # Calculate probability using normal distribution
        probability = norm.cdf(z_score)

        return round(probability, 4)

    def calculate_duration_for_probability(self, target_probability):
        """
        Calculate the project duration corresponding to a given completion probability
        """
        if not self.G:
            raise ValueError("No network graph available. Run analysis first.")

        # Validate probability
        if not (0 <= target_probability <= 1):
            raise ValueError("Probability must be between 0 and 1")

        # Get project expected duration
        project_duration = max([self.G.nodes[node]['EF']
                               for node in self.G.nodes()])

        if self.project_std == 0:
            # No variance in critical path
            return project_duration

        # Calculate Z-score for the given probability
        z_score = norm.ppf(target_probability)

        # Calculate duration
        duration = project_duration + (z_score * self.project_std)

        return round(duration, 2)

    def get_project_statistics(self):
        """Get project statistics for display"""
        if not self.G:
            return None

        # CRITICAL FIX: Calculate expected duration from critical path, not EF
        # values
        if self.critical_paths and self.critical_paths[0]:
            # Calculate expected duration from critical path expected times
            expected_duration = 0
            critical_path = self.critical_paths[0]

            for activity in critical_path:
                if activity in self.G.nodes and activity not in [
                        'START', 'END']:
                    expected_duration += self.G.nodes[activity]['expected_time']
        else:
            # Fallback to EF calculation if no critical path
            expected_duration = max([self.G.nodes[node]['EF']
                                    for node in self.G.nodes()])

        return {
            'expected_duration': round(
                expected_duration,
                3),
            'variance': self.project_variance,
            'std_deviation': self.project_std,
            'critical_path': self.critical_paths[0] if self.critical_paths and self.critical_paths[0] else [],
            'critical_activities_variance': self.get_critical_activities_variance()}

    def get_critical_activities_variance(self):
        """Get variance information for critical activities"""
        if not self.G or not self.critical_paths or not self.critical_paths[0]:
            return []

        critical_activities_info = []
        for activity in self.critical_paths[0]:
            if activity in self.G.nodes and activity not in ['START', 'END']:
                critical_activities_info.append({
                    'id': activity,
                    'variance': self.G.nodes[activity]['variance'],
                    'expected_time': self.G.nodes[activity]['expected_time_ceil']
                })

        return critical_activities_info

    def build_cpm_schedule_table(self, df_gantt, resource_limit):
        """
        Build the initial CPM-based schedule table for PERT analysis.
        This is a wrapper that uses expected_time as duration.
        """
        # For PERT, we use expected_time as the duration
        # The df_gantt should already have expected times in the duration
        # column

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
        import pandas as pd
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
        Apply RCPS heuristic and build the actual schedule table for PERT analysis.
        This uses expected_time as duration.
        """
        import pandas as pd
        import numpy as np

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

        # After scheduling, get the actual PERT project duration
        actual_project_duration = max(
            [tasks.at[tid, 'actual_finish'] for tid in tasks.index])

        # Build time columns based on actual PERT duration
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

        # Calculate resource_scheduled AFTER all activities are filled
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

    def crash_project(
            self,
            target_duration,
            max_iterations=300,
            max_budget=None):
        """
        Crash the project to achieve target duration for PERT analysis.
        This operates on expected_time (ceiling values) as durations.
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

        # Perform initial analysis to get baseline
        crashed_G = self.forward_pass(crashed_G)
        crashed_G = self.backward_pass(crashed_G)
        crashed_G = self.calculate_float(crashed_G)

        # Get initial project duration - only from nodes that have EF values
        ef_values = []
        for node in crashed_G.nodes():
            if 'EF' in crashed_G.nodes[node]:
                ef_values.append(crashed_G.nodes[node]['EF'])

        if not ef_values:
            raise ValueError(
                "No activities found with EF values. Check graph structure.")

        current_duration = max(ef_values)
        iteration = 0

        while current_duration > target_duration and iteration < max_iterations:
            # Budget check before any crash
            if max_budget is not None and total_crash_cost >= max_budget:
                break

            iteration += 1

            # Recalculate PERT analysis on current graph
            crashed_G = self.forward_pass(crashed_G)
            crashed_G = self.backward_pass(crashed_G)
            crashed_G = self.calculate_float(crashed_G)

            # Find critical activities
            critical_activities = [
                node for node in crashed_G.nodes() if crashed_G.nodes[node].get(
                    'float', float('inf')) == 0 and node not in [
                    'START', 'END']]

            if not critical_activities:
                break

            # Find crashable activities on critical path
            crashable_activities = []
            for activity in critical_activities:
                current_dur = crashed_G.nodes[activity].get('duration', 0)
                min_dur = crashed_G.nodes[activity].get(
                    'min_duration', current_dur)
                crash_cost = crashed_G.nodes[activity].get('crash_cost', 0)
                max_steps = max_crash_steps.get(activity, None)
                crashed_so_far = crash_counts.get(activity, 0)

                # Only allow if all conditions are met
                can_crash = (current_dur > min_dur and
                             crash_cost > 0 and
                             (max_steps is None or crashed_so_far < max_steps))

                if can_crash:
                    crashable_activities.append({
                        'id': activity,
                        'crash_cost': crash_cost,
                        'current_duration': current_dur,
                        'min_duration': min_dur
                    })

            if not crashable_activities:
                break

            # Select activity with lowest crash cost
            cheapest_activity = min(
                crashable_activities,
                key=lambda x: x['crash_cost'])
            activity_id = cheapest_activity['id']

            # Budget check before this crash
            if max_budget is not None and total_crash_cost + \
                    cheapest_activity['crash_cost'] > max_budget:
                break

            # Crash the selected activity
            crashed_G.nodes[activity_id]['duration'] -= 1
            total_crash_cost += cheapest_activity['crash_cost']
            crash_counts[activity_id] += 1

            crash_log.append({
                'iteration': iteration,
                'activity': activity_id,
                'crash_cost': cheapest_activity['crash_cost'],
                'new_duration': crashed_G.nodes[activity_id]['duration'],
                'original_duration': original_durations[activity_id]
            })

            # Update project duration
            crashed_G = self.forward_pass(crashed_G)

            # Safely get new duration
            ef_values = []
            for node in crashed_G.nodes():
                if 'EF' in crashed_G.nodes[node]:
                    ef_values.append(crashed_G.nodes[node]['EF'])

            new_duration = max(ef_values) if ef_values else current_duration
            current_duration = new_duration

            if current_duration <= target_duration:
                break

        # Final analysis calculation
        crashed_G = self.forward_pass(crashed_G)
        crashed_G = self.backward_pass(crashed_G)
        crashed_G = self.calculate_float(crashed_G)

        return crashed_G, total_crash_cost, crash_log

    def crash_project_with_rcps(
            self,
            target_duration,
            resource_limit,
            priority_rule='minimum_slack',
            max_iterations=300,
            max_budget=None):
        """
        Crash the project to achieve target duration while respecting resource constraints for PERT analysis.
        This operates on expected_time (ceiling values) as durations.
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

        while iteration < max_iterations:

            # Budget check before any crash
            if max_budget is not None and total_crash_cost >= max_budget:
                break

            iteration += 1

            # Generate RCPS schedule for current graph state
            current_schedule = self.generate_rcps_schedule_for_graph(
                crashed_G, resource_limit, priority_rule)
            current_duration = current_schedule['project_duration']

            # Check if target is achieved
            if current_duration <= target_duration:
                break

            # Find critical activities using zero float approach
            crashed_G_temp = self.forward_pass(crashed_G.copy())
            crashed_G_temp = self.backward_pass(crashed_G_temp)
            crashed_G_temp = self.calculate_float(crashed_G_temp)

            # Get critical activities (activities with zero float)
            critical_activities = [node for node in crashed_G_temp.nodes(
            ) if crashed_G_temp.nodes[node]['float'] == 0 and node not in ['START', 'END']]

            if not critical_activities:
                break

            # Test crash impact for each critical activity
            crash_options = []
            for activity in critical_activities:
                # Get current activity data
                current_dur = crashed_G.nodes[activity]['duration']
                min_dur = crashed_G.nodes[activity]['min_duration']
                crash_cost = crashed_G.nodes[activity]['crash_cost']
                max_steps = max_crash_steps.get(activity, None)
                crashed_so_far = crash_counts.get(activity, 0)

                # Only allow if all conditions are met
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
                        'efficiency': duration_reduction / crash_cost if crash_cost > 0 else 0
                    })

            if not crash_options:
                break

            # Select activity with lowest crash cost
            cheapest_activity = min(
                crash_options, key=lambda x: x['crash_cost'])
            activity_id = cheapest_activity['id']

            # Budget check before this specific crash
            if max_budget is not None and total_crash_cost + \
                    cheapest_activity['crash_cost'] > max_budget:
                break

            # Crash the selected activity
            crashed_G.nodes[activity_id]['duration'] -= 1
            total_crash_cost += cheapest_activity['crash_cost']
            crash_counts[activity_id] += 1

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

        # Generate final RCPS schedule for the crashed graph
        final_schedule = self.generate_rcps_schedule_for_graph(
            crashed_G, resource_limit, priority_rule)
        final_duration = final_schedule['project_duration']

        # Update the crashed graph with final RCPS times
        for activity_id, activity_data in final_schedule['activities'].items():
            if activity_id in crashed_G.nodes:
                crashed_G.nodes[activity_id]['ES'] = activity_data['actual_start']
                crashed_G.nodes[activity_id]['EF'] = activity_data['actual_finish']

        # Calculate LS, LF, and float based on RCPS schedule
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

        return crashed_G, total_crash_cost, crash_log

    def generate_rcps_schedule_for_graph(
            self, G, resource_limit, priority_rule='minimum_slack'):
        """
        Generate RCPS schedule for a given graph state and return schedule data for PERT analysis.
        This uses expected_time as duration.
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

                # Use current durations from the graph (expected_time ceiling
                # values)
                current_duration = G.nodes[node]['duration']

                activities_data.append({
                    'id': node,
                    'duration': current_duration,
                    'resource': G.nodes[node].get('resource_demand', 0),
                    'early_start': 0,
                    'late_finish': 0,
                    'float': 0,
                    'predecessors': predecessors_str
                })

        import pandas as pd
        df_gantt = pd.DataFrame(activities_data)

        # Run CPM analysis first to get ES, LF, float for RCPS
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

        # Run RCPS scheduling
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

        # Use critical activities from zero float calculation
        critical_activities = [node for node in temp_G.nodes(
        ) if temp_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]

        return {
            'project_duration': project_duration,
            'activities': activities,
            'critical_activities': critical_activities
        }

    def build_network_for_rcps(self, activities):
        """
        Build a directed graph network from activity data for PERT RCPS analysis.
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
                    'resource_demand', 0))

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
