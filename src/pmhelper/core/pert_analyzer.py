#!/usr/bin/env python3
"""
PERT Analyzer Module

Handles probabilistic analysis for project management using Program Evaluation
and Review Technique (PERT). Works with optimistic, most likely, and pessimistic
time estimates.
"""

import numpy as np
import networkx as nx
import math
import pandas as pd

# Make scipy import optional for PyInstaller compatibility
try:
    from scipy.stats import norm
    SCIPY_AVAILABLE = True
except ImportError:
    # Fallback: Simple normal distribution approximation
    SCIPY_AVAILABLE = False

    class FallbackNorm:
        @staticmethod
        def cdf(x):
            # Simple normal CDF approximation using error function
            return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    norm = FallbackNorm()

from .network_builder import NetworkBuilder


class PERTAnalyzer:
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
        pred_map = {tid: [p.strip() for p in str(tasks.at[tid, 'predecessors']).split(
            ',') if p.strip() and p.strip() != 'nan'] for tid in tasks.index}
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
    """PERT analysis functionality for probabilistic project management"""

    def __init__(self):
        self.G = None
        self.critical_paths = []
        self.critical_activities = []
        self.project_variance = 0
        self.project_std = 0
        self.network_builder = NetworkBuilder()

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

            # Store both unrounded and rounded values
            # For CPM calculations, we still need to use integers, but store
            # the precise value too
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
                'expected_time': expected_time,  # Store precise value
                'expected_duration': expected_time,  # Add this field for GUI compatibility
                'expected_time_ceil': expected_time_ceil,
                'variance': variance_rounded,
                # Use precise value instead of ceiling for more accurate
                # results
                'duration': expected_time,
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

    def calculate_project_variance(self, G, critical_path):
        """Calculate the total project variance based on critical path activities"""
        total_variance = 0
        if critical_path:
            for activity in critical_path:
                if activity in G.nodes and activity not in ['START', 'END']:
                    total_variance += G.nodes[activity]['variance']

        return round(total_variance, 3)

    def analyze(self, activities_data):
        """Perform comprehensive PERT/CPM analysis with two-phase calculation"""
        try:
            # Load activities with PERT data
            activities = self.load_activities_from_pert_data(activities_data)

            # Phase 2: Calculate scheduling values (integer-based) first to get
            # correct critical path
            scheduling_results = self.calculate_scheduling_values(activities)

            # Phase 1: Calculate statistical values using the scheduling
            # critical path
            statistical_results = self.calculate_statistical_values(
                activities, scheduling_results['critical_paths'])

            # Store results for other methods
            self.G = scheduling_results['network']
            self.critical_paths = scheduling_results['critical_paths']
            self.critical_activities = scheduling_results['critical_activities']
            self.project_variance = statistical_results['project_variance']
            self.project_std = statistical_results['project_std_dev']

            # 🔧 FIX: Store activities for RCPS/Crashing integration
            self.activities = activities

            # Return combined results
            return scheduling_results['network'], scheduling_results['critical_paths'], scheduling_results['critical_activities']

        except Exception as e:
            print(f"Error in PERT analysis: {str(e)}")
            raise

    def calculate_statistical_values(
            self, activities, critical_paths_from_scheduling):
        """Phase 1: Calculate precise statistical values for PERT analysis using scheduling critical path"""
        # Calculate PERT statistics with precise values using critical path
        # from scheduling
        if activities and critical_paths_from_scheduling and critical_paths_from_scheduling[
                0]:
            # Build a network with precise expected times for variance lookup
            statistical_network = self.build_network(activities)

            # Use the critical path determined by scheduling (integer-based) for variance calculation
            # This ensures variance is calculated on the actual project
            # critical path
            critical_path = critical_paths_from_scheduling[0]
            project_variance = self.calculate_project_variance(
                statistical_network, critical_path)
            project_std_dev = round(np.sqrt(project_variance), 3)
        else:
            project_variance = 0
            project_std_dev = 0

        return {
            'project_variance': project_variance,
            'project_std_dev': project_std_dev
        }

    def calculate_scheduling_values(self, activities):
        """Phase 2: Calculate integer-based scheduling values using CPM"""
        # Create activities with rounded-up durations for scheduling
        scheduling_activities = []
        for activity in activities:
            scheduled_activity = activity.copy()
            # Use ceiling of expected time for all scheduling calculations
            scheduled_activity['duration'] = math.ceil(
                activity['expected_time'])
            scheduled_activity['expected'] = math.ceil(
                activity['expected_time'])  # For display
            scheduling_activities.append(scheduled_activity)

        # Build network for critical path analysis with integer durations
        network = self.build_network(scheduling_activities)
        network = self.network_builder.forward_pass(network)
        network = self.network_builder.backward_pass(network)
        network = self.network_builder.calculate_float(network)
        critical_paths, critical_activities = self.network_builder.identify_critical_path(
            network)

        return {
            'network': network,
            'critical_paths': critical_paths,
            'critical_activities': critical_activities
        }

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

        # Calculate expected duration from critical path expected times
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
    
    def get_risk_analysis_input(self) -> dict:
        """
        Prepare data for risk analysis modules.
        
        Returns structured PERT results suitable for DelayRiskAnalyzer,
        ContingencyPlanner, VarianceReductionAnalyzer, and ActivityRiskPrioritizer.
        
        Returns:
            Dict with:
                - expected_duration: Project expected completion time
                - variance: Project variance
                - std_deviation: Project standard deviation
                - critical_path: List of critical path activity IDs
                - activities: Dict of activity data with full details
                - network: NetworkX graph (optional)
        """
        if not self.G:
            raise ValueError("No analysis results available. Run analyze() first.")
        
        # Get project statistics
        stats = self.get_project_statistics()
        if not stats:
            raise ValueError("Unable to retrieve project statistics")
        
        # Build activities dictionary with detailed information
        activities_dict = {}
        for node_id in self.G.nodes():
            if node_id not in ['START', 'END']:
                node_data = self.G.nodes[node_id]
                activities_dict[node_id] = {
                    'id': node_id,
                    'activity': node_data.get('activity', ''),
                    'expected_time': node_data.get('expected_time', 0),
                    'expected_duration': node_data.get('expected_time', 0),
                    'variance': node_data.get('variance', 0),
                    'optimistic': node_data.get('optimistic', 0),
                    'most_likely': node_data.get('most_likely', 0),
                    'pessimistic': node_data.get('pessimistic', 0),
                    'early_start': node_data.get('ES', 0),
                    'early_finish': node_data.get('EF', 0),
                    'late_start': node_data.get('LS', 0),
                    'late_finish': node_data.get('LF', 0),
                    'float': node_data.get('TF', 0),
                    'total_float': node_data.get('TF', 0),
                    'normal_cost': node_data.get('normal_cost', 0),
                    'cost': node_data.get('normal_cost', 0),
                    'crash_cost': node_data.get('crash_cost', 0),
                    'resource_demand': node_data.get('resource_demand', 0),
                    'min_duration': node_data.get('min_duration', 1)
                }
        
        return {
            'expected_duration': stats['expected_duration'],
            'variance': stats['variance'],
            'std_deviation': stats['std_deviation'],
            'critical_path': stats['critical_path'],
            'activities': activities_dict,
            'network': self.G
        }
    
    def analyze_delay_risk(
        self,
        contract_time: float,
        penalty_rate: float,
        max_penalty_percent: float = 0.20,
        contract_value: float = None
    ) -> dict:
        """
        Convenience method for delay risk analysis.
        
        Args:
            contract_time: Contracted completion deadline
            penalty_rate: Penalty cost per time unit of delay
            max_penalty_percent: Maximum penalty as fraction of contract (default 20%)
            contract_value: Contract value for penalty cap (optional)
        
        Returns:
            Risk analysis results from DelayRiskAnalyzer
        """
        from .risk_analysis import DelayRiskAnalyzer
        
        risk_input = self.get_risk_analysis_input()
        analyzer = DelayRiskAnalyzer(risk_input)
        return analyzer.calculate_risk_cost(
            contract_time,
            penalty_rate,
            max_penalty_percent,
            contract_value
        )
    
    def estimate_contingency(
        self,
        confidence_level: float = 0.95,
        daily_cost_rate: float = None
    ) -> dict:
        """
        Convenience method for contingency planning.
        
        Args:
            confidence_level: Desired probability of completion (0.5 to 0.999)
            daily_cost_rate: Cost per time unit (optional)
        
        Returns:
            Contingency planning results from ContingencyPlanner
        """
        from .risk_analysis import ContingencyPlanner
        
        risk_input = self.get_risk_analysis_input()
        planner = ContingencyPlanner(risk_input)
        return planner.calculate_contingency(confidence_level, daily_cost_rate)
    
    def analyze_variance_reduction_strategies(
        self,
        contract_time: float,
        penalty_rate: float,
        time_reduction_cost: float,
        variance_reduction_cost: float,
        max_budget: float = None
    ) -> dict:
        """
        Convenience method for variance reduction strategy analysis.
        
        Args:
            contract_time: Contract deadline
            penalty_rate: Penalty per time unit
            time_reduction_cost: Cost per unit time reduction
            variance_reduction_cost: Cost per unit variance reduction
            max_budget: Maximum budget for improvements (optional)
        
        Returns:
            Strategy comparison results from VarianceReductionAnalyzer
        """
        from .risk_analysis import VarianceReductionAnalyzer
        
        risk_input = self.get_risk_analysis_input()
        analyzer = VarianceReductionAnalyzer(risk_input)
        return analyzer.analyze_strategies(
            contract_time,
            penalty_rate,
            time_reduction_cost,
            variance_reduction_cost,
            max_budget
        )
    
    def prioritize_activity_risks(self) -> pd.DataFrame:
        """
        Convenience method for activity risk prioritization.
        
        Returns:
            DataFrame with activity risk scores and recommendations
        """
        from .risk_analysis import ActivityRiskPrioritizer
        
        risk_input = self.get_risk_analysis_input()
        prioritizer = ActivityRiskPrioritizer(risk_input)
        return prioritizer.calculate_risk_scores()
    
    def generate_risk_mitigation_plan(
        self,
        budget_available: float = None,
        focus_critical_path: bool = True
    ) -> dict:
        """
        Convenience method for generating mitigation plan.
        
        Args:
            budget_available: Budget available for mitigation (optional)
            focus_critical_path: Prioritize critical path activities
        
        Returns:
            Comprehensive mitigation plan from ActivityRiskPrioritizer
        """
        from .risk_analysis import ActivityRiskPrioritizer
        
        risk_input = self.get_risk_analysis_input()
        prioritizer = ActivityRiskPrioritizer(risk_input)
        return prioritizer.generate_mitigation_plan(budget_available, focus_critical_path)
