
    def generate_rcps_schedule_for_graph(self, G, resource_limit, priority_rule='minimum_slack'):
        """
        Generate RCPS schedule for any graph state during crashing evaluation.
        
        This method is the foundation of the enhanced crashing approach. It converts
        a NetworkX graph to RCPS schedule format and returns comprehensive schedule data.
        
        Args:
            G (networkx.DiGraph): Project network graph with current durations
            resource_limit (int): Maximum resource availability per time period
            priority_rule (str): RCPS scheduling rule ('minimum_slack', 'shortest_duration', etc.)
        
        Returns:
            dict: {
                'project_duration': int,
                'activities': dict,  # activity_id -> {actual_start, actual_finish, resource_used}
                'critical_activities': list,
                'resource_usage': dict,  # time_period -> resource_used
                'schedule_feasible': bool
            }
        """
        try:
            # STEP 1: Convert NetworkX graph to DataFrame format
            activities_data = []
            for node in G.nodes():
                if node not in ['START', 'END']:
                    # Extract predecessors (excluding START)
                    predecessors = [pred for pred in G.predecessors(node) if pred != 'START']
                    pred_str = ','.join(predecessors) if predecessors else ''
                    
                    activities_data.append({
                        'id': node,
                        'duration': G.nodes[node].get('duration', 1),
                        'resource': G.nodes[node].get('resource_demand', 1),
                        'early_start': G.nodes[node].get('ES', 0),
                        'late_finish': G.nodes[node].get('LF', 0),
                        'float': G.nodes[node].get('float', 0),
                        'predecessors': pred_str,
                        'crash_cost': G.nodes[node].get('crash_cost', 100),
                        'normal_cost': G.nodes[node].get('normal_cost', 50),
                        'min_duration': G.nodes[node].get('min_duration', 1)
                    })
            
            if not activities_data:
                return {
                    'project_duration': 0,
                    'activities': {},
                    'critical_activities': [],
                    'resource_usage': {},
                    'schedule_feasible': False
                }
            
            # STEP 2: Create DataFrame for RCPS processing
            import pandas as pd
            df_gantt = pd.DataFrame(activities_data)
            
            # STEP 3: Use existing RCPS analyzer methods
            # Note: This requires integration with existing RCPSAnalyzer
            # For now, return a mock schedule structure
            
            # TODO: Integrate with actual RCPS scheduling logic
            # This would use self.base_analyzer or create temporary RCPSAnalyzer
            
            # STEP 4: Return comprehensive schedule data
            mock_schedule = {
                'project_duration': max([act['early_start'] + act['duration'] for act in activities_data]),
                'activities': {
                    act['id']: {
                        'actual_start': act['early_start'],
                        'actual_finish': act['early_start'] + act['duration'],
                        'resource_used': act['resource']
                    } for act in activities_data
                },
                'critical_activities': [act['id'] for act in activities_data if act['float'] == 0],
                'resource_usage': {},  # TODO: Calculate actual resource usage per time period
                'schedule_feasible': True
            }
            
            return mock_schedule
            
        except Exception as e:
            print(f"Error in generate_rcps_schedule_for_graph: {e}")
            return {
                'project_duration': 0,
                'activities': {},
                'critical_activities': [],
                'resource_usage': {},
                'schedule_feasible': False
            }
    