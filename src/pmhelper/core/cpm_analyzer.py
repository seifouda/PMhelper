#!/usr/bin/env python3
"""
Critical Path Method (CPM) Analyzer

Core CPM analysis functionality including project scheduling, crashing optimization,
and resource-constrained project scheduling (RCPS).
"""

import networkx as nx
import pandas as pd
import numpy as np
from collections import defaultdict

from .network_builder import NetworkBuilder


class CPMAnalyzer:
    """Core CPM analysis functionality"""
    
    def __init__(self):
        self.G = None
        self.critical_paths = []
        self.critical_activities = []
        self.network_builder = NetworkBuilder()
    
    def load_activities_from_data(self, activities_data):
        """Load activities from list of dictionaries"""
        activities = []
        
        for row in activities_data:
            # Convert duration to integer
            try:
                duration = int(row['duration'])
            except (ValueError, KeyError):
                raise ValueError(f"Duration for activity {row.get('id', 'Unknown')} must be a number")
            
            # Handle crash duration and cost    
            try:
                min_duration = int(row.get('min_duration', duration))  # Default to normal duration
                if min_duration > duration:
                    min_duration = duration  # Ensure min_duration <= duration
            except (ValueError, TypeError):
                min_duration = duration
            
            try:
                crash_cost = float(row.get('crash_cost', 0))
            except (ValueError, TypeError):
                crash_cost = 0
            
            # Process predecessors - handle both list and string formats
            predecessors = []
            pred_data = row.get('predecessors')
            if pred_data:
                if isinstance(pred_data, list):
                    # Already a list - use directly
                    predecessors = [p.strip() for p in pred_data if p and str(p).strip()]
                elif isinstance(pred_data, str) and pred_data.strip():
                    # Comma-separated string - split it
                    predecessors = [p.strip() for p in pred_data.split(',') if p.strip()]
                else:
                    # Convert to string and split (fallback for other types)
                    predecessors = [p.strip() for p in str(pred_data).split(',') if p.strip()]
            
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
    
    def analyze(self, activities_data):
        """Perform complete CPM analysis"""
        activities = self.load_activities_from_data(activities_data)
        # Store activities in analyzer for RCPS crashing access
        self.activities = activities
        self.G = self.network_builder.build_network(activities)
        self.G = self.network_builder.forward_pass(self.G)
        self.G = self.network_builder.backward_pass(self.G)
        self.G = self.network_builder.calculate_float(self.G)
        self.critical_paths, self.critical_activities = self.network_builder.identify_critical_path(self.G)
        self.G = self.network_builder.calculate_additional_metrics(self.G, activities_data)
        self.critical_paths, self.critical_activities = self.network_builder.identify_critical_path(self.G)
    
        return self.G, self.critical_paths, self.critical_activities
    
    def build_cpm_schedule_table(self, df_gantt, resource_limit):
        """
        Build the initial CPM-based schedule table.
        Returns: DataFrame (table), list of time units, dict of critical activities
        """
        df = df_gantt.copy()
        # Ensure correct columns
        required = ['id', 'duration', 'resource', 'early_start', 'late_finish', 'float', 'predecessors']
        for col in required:
            if col not in df.columns:
                raise ValueError(f"Missing column: {col}")
        df['critical'] = df['float'] == 0
        # Time units: from 1 to max LF
        max_time = int(df['late_finish'].max())
        time_cols = list(range(1, max_time + 1))
        # Build table
        table = df[['id', 'duration', 'resource', 'early_start', 'late_finish', 'float']].copy()
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
        resource_row = pd.Series(['RA', '', resource_limit, '', '', ''] + resource_available, index=table.columns)
        scheduled_row = pd.Series(['RS', '', '', '', '', ''] + resource_scheduled, index=table.columns)
        table = pd.concat([table, pd.DataFrame([resource_row, scheduled_row])], ignore_index=True)
        return table, time_cols, set(df[df['critical']]['id'])
    
    def rcps_heuristic_schedule_table(self, df_gantt, resource_limit, priority_rule='minimum_slack'):
        """
        Apply RCPS heuristic and build the actual schedule table.
        Returns: DataFrame (table), dict of actual start times, dict of critical activities
        """
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
        pred_map = {tid: [p for p in str(tasks.at[tid, 'predecessors']).split(',') if p and p != 'nan'] for tid in tasks.index}
        
        # Scheduling loop
        while unscheduled:
            # Find ready tasks
            ready = []
            for tid in unscheduled:
                preds = pred_map[tid]
                if all(tasks.at[p, 'scheduled'] and tasks.at[p, 'actual_finish'] <= current_time for p in preds):
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
        actual_project_duration = max([tasks.at[tid, 'actual_finish'] for tid in tasks.index])

        # Build time columns based on actual RCPS duration
        time_cols = list(range(1, actual_project_duration + 1))
        
        # Build table
        table = tasks.reset_index()[['id', 'duration', 'resource', 'early_start', 'late_finish', 'float', 'actual_start']].copy()
        
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
        resource_row = pd.Series(['RA', '', '', '', '', '', ''] + resource_available, index=table.columns)
        scheduled_row = pd.Series(['RS', '', '', '', '', '', ''] + resource_scheduled, index=table.columns)
        table = pd.concat([table, pd.DataFrame([resource_row, scheduled_row])], ignore_index=True)
        
        # Build actual start dict for highlighting
        actual_starts = {row['id']: row['actual_start'] for _, row in table.iterrows() if row['id'] not in ['RA', 'RS']}
        # Replace all nan and "nan" with empty string
        table = table.replace({np.nan: '', 'nan': ''})
        
        return table, actual_starts, set(df[df['critical']]['id'])
    
    def get_scheduled_critical_path(self, scheduled_activities):
        """
        Find the path with the longest finish time in the scheduled activities.
        Returns a list of activity IDs on the critical path.
        """
        # Build a graph from scheduled_activities using their dependencies
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
        
        return set(max_path)
    
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
                G_new.nodes[node]['EF'] = rcps_start_times[node] + G_new.nodes[node]['duration']
        
        # Calculate project duration
        project_duration = max([G_new.nodes[node]['EF'] for node in G_new.nodes()])
        
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
                    min_succ_ls = min([G_new.nodes[succ]['LS'] for succ in successors])
                    G_new.nodes[node]['LF'] = min_succ_ls
                else:
                    G_new.nodes[node]['LF'] = project_duration
                
                # Calculate LS
                G_new.nodes[node]['LS'] = G_new.nodes[node]['LF'] - duration
                
                # Calculate float
                G_new.nodes[node]['float'] = G_new.nodes[node]['LS'] - G_new.nodes[node]['ES']
        
        return G_new
    
    def crash_project(self, target_duration, max_iterations=300, max_budget=None):
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
        original_durations = {node: self.G.nodes[node]['duration'] for node in self.G.nodes()}
        
        # Create a copy of the graph to modify
        crashed_G = self.G.copy()
        total_crash_cost = 0
        crash_log = []
        
        # Track how many times each activity has been crashed
        crash_counts = {node: 0 for node in crashed_G.nodes()}

        # Get max_crash_steps for each activity (default: unlimited)
        max_crash_steps = {}
        for node in crashed_G.nodes():
            max_crash_steps[node] = crashed_G.nodes[node].get('max_crash_steps', None)
        
        # Get initial project duration
        current_duration = max([crashed_G.nodes[node]['EF'] for node in crashed_G.nodes()])
        iteration = 0
        
        # Initialize simulation time - starts at 0 (beginning of project)
        current_time = 0
        # Initialize set to track completed activities
        completed_activities = set()
        
        print(f"Starting crash optimization: Initial duration = {current_duration}, Target = {target_duration}")
        
        while current_duration > target_duration and iteration < max_iterations:
            
            # Budget check before any crash
            if max_budget is not None and total_crash_cost >= max_budget:
                print(f"Crash budget reached: {total_crash_cost} >= {max_budget}")
                break
            
            iteration += 1
            
            # Recalculate CPM on current graph
            crashed_G = self.network_builder.forward_pass(crashed_G)
            crashed_G = self.network_builder.backward_pass(crashed_G)
            crashed_G = self.network_builder.calculate_float(crashed_G)
            
            # Find critical activities
            critical_activities = [node for node in crashed_G.nodes() 
                                if crashed_G.nodes[node]['float'] == 0 and node not in ['START', 'END']]
            
            print(f"Iteration {iteration}: Critical path = {' -> '.join(critical_activities)}")
            print(f"Current simulation time = {current_time}")
            
            # Update completed activities based on current simulation time
            for node in crashed_G.nodes():
                if node not in ['START', 'END']:
                    ef = crashed_G.nodes[node]['EF']
                    if ef <= current_time:
                        completed_activities.add(node)
                        print(f"DEBUG: Activity {node} completed at time {ef} (current_time: {current_time})")
            
            print(f"Completed activities: {sorted(list(completed_activities))}")
            
            if not critical_activities:
                print("No critical activities found. Breaking.")
                break
            
            # Find activities that can be crashed (on critical path, not completed, have crash potential)
            crashable_activities = []
            for act in critical_activities:
                if (act not in completed_activities and 
                    crashed_G.nodes[act]['duration'] > crashed_G.nodes[act]['min_duration'] and
                    crashed_G.nodes[act]['crash_cost'] > 0):
                    
                    # Determine if in progress or future
                    es = crashed_G.nodes[act]['ES']
                    ef = crashed_G.nodes[act]['EF']
                    is_in_progress = es <= current_time and ef > current_time
                    
                    # Check max_crash_steps limit
                    max_steps = max_crash_steps.get(act, None)
                    crashed_so_far = crash_counts.get(act, 0)
                    
                    if max_steps is None or crashed_so_far < max_steps:
                        crashable_activities.append({
                            'id': act,
                            'crash_cost': crashed_G.nodes[act]['crash_cost'],
                            'duration': crashed_G.nodes[act]['duration'],
                            'min_duration': crashed_G.nodes[act]['min_duration'],
                            'is_in_progress': is_in_progress
                        })
            
            # Sort by priority (in-progress first, then by cost)
            in_progress = [a for a in crashable_activities if a['is_in_progress']]
            future = [a for a in crashable_activities if not a['is_in_progress']]
            
            in_progress.sort(key=lambda x: x['crash_cost'])
            future.sort(key=lambda x: x['crash_cost'])
            
            # Combine with priority to in-progress activities
            crashable_activities = in_progress + future
            
            if not crashable_activities:
                print("No more activities can be crashed. Breaking.")
                break
            
            # Prioritize in-progress activities over future activities
            cheapest_activity = min(crashable_activities, key=lambda x: x['crash_cost'])
            activity_id = cheapest_activity['id']
            
            # Add logging for clarity about selection
            if cheapest_activity['is_in_progress']:
                print(f"  Selected activity {activity_id} (in progress) with lowest cost {cheapest_activity['crash_cost']}")
            else:
                print(f"  Selected activity {activity_id} (future) with lowest cost {cheapest_activity['crash_cost']}")
            
            activity_id = cheapest_activity['id']
            
            # Budget check before this crash
            if max_budget is not None and total_crash_cost + cheapest_activity['crash_cost'] > max_budget:
                print(f"Next crash would exceed budget: {total_crash_cost} + {cheapest_activity['crash_cost']} > {max_budget}")
                break
            
            # Crash the selected activity
            crashed_G.nodes[activity_id]['duration'] -= 1
            total_crash_cost += cheapest_activity['crash_cost']
            crash_counts[activity_id] += 1  # Track this crash
            
            print(f"  Crashing {activity_id}: {cheapest_activity['duration']} → {crashed_G.nodes[activity_id]['duration']} (Cost: {cheapest_activity['crash_cost']})")
            
            crash_log.append({
                'iteration': iteration,
                'activity': activity_id,
                'crash_cost': cheapest_activity['crash_cost'],
                'new_duration': crashed_G.nodes[activity_id]['duration'],
                'original_duration': original_durations[activity_id]
            })
            
            # Update project duration
            crashed_G = self.network_builder.forward_pass(crashed_G)
            crashed_G = self.network_builder.backward_pass(crashed_G)
            crashed_G = self.network_builder.calculate_float(crashed_G)
            
            new_duration = max([crashed_G.nodes[node]['EF'] for node in crashed_G.nodes()])
            print(f"  New project duration: {current_duration} → {new_duration}")
            current_duration = new_duration
            
            # CRITICAL FIX: Uniformly advance time by 1 unit
            current_time += 1
            print(f"  Advanced time to {current_time}")
                
            if current_duration <= target_duration:
                print(f"Target duration {target_duration} achieved!")
                break
            
        # Final CPM calculation
        crashed_G = self.network_builder.forward_pass(crashed_G)
        crashed_G = self.network_builder.backward_pass(crashed_G)
        crashed_G = self.network_builder.calculate_float(crashed_G)
        
        print(f"Crash optimization complete. Final duration: {current_duration}, Total cost: {total_crash_cost}")
        
        return crashed_G, total_crash_cost, crash_log
