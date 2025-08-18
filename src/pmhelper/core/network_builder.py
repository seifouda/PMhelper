#!/usr/bin/env python3
"""
Network Builder Module

Provides utilities for building and manipulating project network graphs.
Contains shared functionality for network construction, graph operations,
and topological analysis.
"""

import networkx as nx
import numpy as np


class NetworkBuilder:
    """Utility class for building and managing project network graphs"""
    
    @staticmethod
    def build_network(activities):
        """
        Build a directed graph network from activity data
        
        Args:
            activities (list): List of activity dictionaries
            
        Returns:
            nx.DiGraph: Directed graph representation of the project network
        """
        # Create directed graph
        G = nx.DiGraph()
        
        # Add all activities as nodes with attributes
        for activity in activities:
            G.add_node(
                activity['id'],
                duration=activity['duration'],
                min_duration=activity.get('min_duration', activity['duration']),
                crash_cost=activity.get('crash_cost', 0),
                activity=activity.get('activity', ''),
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
            G.add_node('START', duration=0, activity='Start')
            for node in start_nodes:
                G.add_edge('START', node)
        
        # Add END node and connect nodes with no successors to it
        end_nodes = [node for node in G.nodes() if G.out_degree(node) == 0 and node != 'START']
        if end_nodes:
            G.add_node('END', duration=0, activity='End')
            for node in end_nodes:
                G.add_edge(node, 'END')
        
        return G
    
    @staticmethod
    def forward_pass(G):
        """
        Perform forward pass to calculate Early Start (ES) and Early Finish (EF)
        
        Args:
            G (nx.DiGraph): Project network graph
            
        Returns:
            nx.DiGraph: Graph with ES and EF attributes updated
        """
        start_activities = [node for node in G.nodes() if G.in_degree(node) == 0]
        
        nx.set_node_attributes(G, 0, 'ES')
        nx.set_node_attributes(G, 0, 'EF')
        
        for node in nx.topological_sort(G):
            duration = G.nodes[node]['duration']
            if node in start_activities:
                G.nodes[node]['ES'] = 0
            else:
                pred_ef = [G.nodes[pred]['EF'] for pred in G.predecessors(node)]
                G.nodes[node]['ES'] = max(pred_ef) if pred_ef else 0
            G.nodes[node]['EF'] = G.nodes[node]['ES'] + duration

        # Ensure END node ES/EF is set as max EF of its predecessors
        if 'END' in G.nodes:
            preds = list(G.predecessors('END'))
            G.nodes['END']['ES'] = max([G.nodes[p]['EF'] for p in preds]) if preds else 0
            G.nodes['END']['EF'] = G.nodes['END']['ES']
        return G
    
    @staticmethod
    def backward_pass(G):
        """
        Perform backward pass to calculate Late Start (LS) and Late Finish (LF)
        
        Args:
            G (nx.DiGraph): Project network graph
            
        Returns:
            nx.DiGraph: Graph with LS and LF attributes updated
        """
        end_activities = [node for node in G.nodes() if G.out_degree(node) == 0]
        
        project_duration = max([G.nodes[node]['EF'] for node in G.nodes()])
        nx.set_node_attributes(G, project_duration, 'LF')
        nx.set_node_attributes(G, project_duration, 'LS')
        
        for node in reversed(list(nx.topological_sort(G))):
            duration = G.nodes[node]['duration']
            
            if node in end_activities:
                G.nodes[node]['LF'] = project_duration
            else:
                succ_ls = [G.nodes[succ]['LS'] for succ in G.successors(node)]
                G.nodes[node]['LF'] = min(succ_ls) if succ_ls else project_duration
            
            G.nodes[node]['LS'] = G.nodes[node]['LF'] - duration
        
        return G
    
    @staticmethod
    def calculate_float(G):
        """
        Calculate float (slack) for each activity
        
        Args:
            G (nx.DiGraph): Project network graph
            
        Returns:
            nx.DiGraph: Graph with float attributes updated
        """
        for node in G.nodes():
            G.nodes[node]['float'] = G.nodes[node]['LS'] - G.nodes[node]['ES']
        return G
    
    @staticmethod
    def identify_critical_path(G):
        """
        Identify the critical path (activities with zero float)
        
        Args:
            G (nx.DiGraph): Project network graph
            
        Returns:
            tuple: (critical_paths, critical_activities)
        """
        critical_activities = [node for node in G.nodes() if G.nodes[node]['float'] == 0]
        critical_subgraph = G.subgraph(critical_activities)
        
        start_nodes = [node for node in critical_subgraph.nodes() if critical_subgraph.in_degree(node) == 0]
        end_nodes = [node for node in critical_subgraph.nodes() if critical_subgraph.out_degree(node) == 0]
        
        longest_path = []
        max_length = 0
        
        for start in start_nodes:
            for end in end_nodes:
                try:
                    paths = list(nx.all_simple_paths(critical_subgraph, start, end))
                    for path in paths:
                        if len(path) > max_length:
                            max_length = len(path)
                            longest_path = path
                except nx.NetworkXNoPath:
                    pass
        
        return [longest_path] if longest_path else [critical_activities], critical_activities
    
    @staticmethod
    def calculate_additional_metrics(G, activities_data):
        """
        Calculate additional metrics for each activity
        
        Args:
            G (nx.DiGraph): Project network graph
            activities_data (list): Original activity data
            
        Returns:
            nx.DiGraph: Graph with additional metrics
        """
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
                        if successor not in ['START', 'END'] and successor not in total_successors:
                            total_successors.add(successor)
                            get_all_successors(successor)
                
                get_all_successors(node)
                G.nodes[node]['num_total_successors'] = len(total_successors)
                
                # Resource demand (from input data if available)
                activity_data = activity_map.get(node, {})
                resource_demand = activity_data.get('resource_demand', 0)
                try:
                    G.nodes[node]['resource_demand'] = int(resource_demand) if resource_demand else 0
                except (ValueError, TypeError):
                    G.nodes[node]['resource_demand'] = 0
                
                # Cumulative demand (resource_demand * duration)
                G.nodes[node]['cumulative_demand'] = G.nodes[node]['resource_demand'] * G.nodes[node]['duration']
                
                # GRPW (Greatest Rank Positional Weight) = duration + sum of durations of all successors
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
