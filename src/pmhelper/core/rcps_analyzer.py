#!/usr/bin/env python3
"""
RCPS Analyzer Module

Provides analysis capabilities specifically for RCPS-based project data.
This analyzer handles resource-constrained project schedules and maintains
compatibility with the existing crashing framework.
"""

import networkx as nx
from typing import Dict, List, Optional, Any
import copy


class RCPSAnalyzer:
    """Analyzer specifically for RCPS-based project data"""

    def __init__(self, rcps_graph, resource_limit, original_analyzer=None):
        """
        Initialize RCPS Analyzer with full compatibility for crashing core

        Args:
            rcps_graph: NetworkX graph with RCPS schedule data
            resource_limit: Maximum available resources
            original_analyzer: Reference to original CPM/PERT analyzer for compatibility
        """
        self.graph = rcps_graph
        self.G = rcps_graph  # Alias for compatibility with crashing code
        self.resource_limit = resource_limit
        self.original_analyzer = original_analyzer

        # Copy activities data from original analyzer if available
        if original_analyzer and hasattr(original_analyzer, 'activities'):
            self.activities = copy.deepcopy(original_analyzer.activities)
            self._update_activities_with_rcps_data()
        else:
            self.activities = self._build_activities_from_graph()

        # Copy network builder from original analyzer for consistency
        if original_analyzer and hasattr(original_analyzer, 'network_builder'):
            self.network_builder = original_analyzer.network_builder
        else:
            # Create a minimal network builder if none available
            self.network_builder = self._create_minimal_network_builder()

    def _update_activities_with_rcps_data(self):
        """Update activities list with RCPS-specific data from graph"""
        for activity in self.activities:
            activity_id = activity.get('id')
            if activity_id in self.graph.nodes():
                node_data = self.graph.nodes[activity_id]
                # Update with RCPS actual start times and resource constraints
                if 'actual_start' in node_data:
                    activity['actual_start'] = node_data['actual_start']
                if 'ES' in node_data:
                    # Should be actual_start for RCPS
                    activity['ES'] = node_data['ES']
                if 'EF' in node_data:
                    activity['EF'] = node_data['EF']

    def _build_activities_from_graph(self):
        """Build activities list from RCPS graph nodes"""
        activities = []
        for node_id, node_data in self.graph.nodes(data=True):
            activity = {
                'id': node_id,
                'duration': node_data.get('duration', 0),
                'resource': node_data.get('resource', 1),
                # Default crash cost
                'crash_cost': node_data.get('crash_cost', 100),
                'min_duration': node_data.get('min_duration', max(1, node_data.get('duration', 0) // 2))
            }

            # Add predecessors
            predecessors = list(self.graph.predecessors(node_id))
            activity['predecessors'] = predecessors

            activities.append(activity)

        return activities

    def _create_minimal_network_builder(self):
        """Create a minimal network builder for RCPS operations"""
        class MinimalNetworkBuilder:
            def forward_pass(self, G):
                """Simple forward pass for RCPS network"""
                # Set earliest start times based on actual_start if available
                for node in nx.topological_sort(G):
                    node_data = G.nodes[node]

                    if 'actual_start' in node_data:
                        # Use actual start time from RCPS
                        G.nodes[node]['ES'] = node_data['actual_start']
                    else:
                        # Calculate based on predecessors
                        if len(list(G.predecessors(node))) == 0:
                            G.nodes[node]['ES'] = 0
                        else:
                            max_ef = max(G.nodes[pred].get('EF', 0)
                                         for pred in G.predecessors(node))
                            G.nodes[node]['ES'] = max_ef

                    # Calculate earliest finish
                    duration = node_data.get('duration', 0)
                    G.nodes[node]['EF'] = G.nodes[node]['ES'] + duration

                return G

            def backward_pass(self, G):
                """Backward pass for RCPS network"""
                # Find project end time
                if G.nodes():
                    project_end = max(
                        G.nodes[node].get(
                            'EF', 0) for node in G.nodes())
                else:
                    project_end = 0

                # Perform backward pass
                for node in reversed(list(nx.topological_sort(G))):
                    node_data = G.nodes[node]

                    if len(list(G.successors(node))) == 0:
                        # Project end activities
                        G.nodes[node]['LF'] = project_end
                    else:
                        # Calculate based on successors
                        min_ls = min(
                            G.nodes[succ].get(
                                'LS', project_end) for succ in G.successors(node))
                        G.nodes[node]['LF'] = min_ls

                    # Calculate latest start
                    duration = node_data.get('duration', 0)
                    G.nodes[node]['LS'] = G.nodes[node]['LF'] - duration

                return G

            def calculate_float(self, G):
                """Calculate float values for RCPS network"""
                for node in G.nodes():
                    es = G.nodes[node].get('ES', 0)
                    ls = G.nodes[node].get('LS', 0)
                    G.nodes[node]['float'] = ls - es

                return G

        return MinimalNetworkBuilder()

    def forward_pass(self, G):
        """Forward pass considering resource constraints and actual start times"""
        return self.network_builder.forward_pass(G)

    def backward_pass(self, G):
        """Backward pass for RCPS network"""
        return self.network_builder.backward_pass(G)

    def calculate_float(self, G):
        """Calculate float in resource-constrained context"""
        return self.network_builder.calculate_float(G)

    def get_critical_path(self):
        """Get critical path from RCPS network"""
        critical_nodes = []
        for node in self.graph.nodes():
            if self.graph.nodes[node].get('float', 1) == 0:
                critical_nodes.append(node)
        return critical_nodes

    def validate_resource_constraints(self, crashed_activities=None):
        """
        Validate that current schedule respects resource constraints

        Args:
            crashed_activities: Dict of {activity_id: new_duration} for crashed activities

        Returns:
            bool: True if constraints are satisfied
        """
        if crashed_activities is None:
            crashed_activities = {}

        # Create timeline of resource usage
        timeline = {}

        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            start_time = int(
                node_data.get(
                    'actual_start',
                    node_data.get(
                        'ES',
                        0)))

            # Use crashed duration if available, otherwise original duration
            if node in crashed_activities:
                duration = crashed_activities[node]
            else:
                duration = int(node_data.get('duration', 0))

            resource_demand = node_data.get('resource', 1)

            # Add resource usage to timeline
            for t in range(start_time, start_time + duration):
                if t not in timeline:
                    timeline[t] = 0
                timeline[t] += resource_demand

        # Check if any time period exceeds resource limit
        for time_period, resource_usage in timeline.items():
            if resource_usage > self.resource_limit:
                return False

        return True
