    # ============================================================================
    # ENHANCED METHODOLOGY FOUNDATION METHODS (PHASE 1)
    # ============================================================================
    
    def generate_rcps_schedule_for_graph(self, G, resource_limit, priority_rule='minimum_slack'):
        """
        Generate RCPS schedule for any graph state during crashing evaluation.
        
        This method is the foundation of the enhanced crashing approach. It converts
        a NetworkX graph to RCPS schedule format and returns comprehensive schedule data.
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
            
            # STEP 3: Use existing RCPS analyzer methods to generate schedule
            if hasattr(self.base_analyzer, 'rcps_heuristic_schedule_table'):
                rcps_table, actual_starts, critical_ids = self.base_analyzer.rcps_heuristic_schedule_table(
                    df_gantt, resource_limit, priority_rule
                )
                
                # Extract schedule data from RCPS table
                activities = {}
                project_duration = 0
                resource_usage = {}
                
                for idx, row in rcps_table.iterrows():
                    if row['id'] not in ['RA', 'RS']:  # Skip resource rows
                        activity_id = row['id']
                        actual_start = row.get('actual_start', row.get('early_start', 0))
                        duration = row.get('duration', 1)
                        actual_finish = actual_start + duration
                        
                        activities[activity_id] = {
                            'actual_start': actual_start,
                            'actual_finish': actual_finish,
                            'resource_used': row.get('resource', 1)
                        }
                        
                        project_duration = max(project_duration, actual_finish)
                
                # Calculate resource usage per time period
                for t in range(1, int(project_duration) + 1):
                    resource_usage[t] = 0
                    for act_id, act_data in activities.items():
                        if act_data['actual_start'] < t <= act_data['actual_finish']:
                            resource_usage[t] += act_data['resource_used']
                
                return {
                    'project_duration': int(project_duration),
                    'activities': activities,
                    'critical_activities': list(critical_ids) if critical_ids else [],
                    'resource_usage': resource_usage,
                    'schedule_feasible': True
                }
            
            else:
                # Fallback: Return mock schedule based on CPM times
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
                    'resource_usage': {},
                    'schedule_feasible': True
                }
                return mock_schedule
            
        except Exception as e:
            print(f"Error in generate_rcps_schedule_for_graph: {e}")
            import traceback
            traceback.print_exc()
            return {
                'project_duration': 0,
                'activities': {},
                'critical_activities': [],
                'resource_usage': {},
                'schedule_feasible': False
            }

    def analyze_activity_status(self, G, current_time):
        """
        Analyze activity execution status at current simulation time.
        
        This method provides sophisticated activity status tracking that distinguishes
        between completed, in-progress, and future activities based on current simulation time.
        """
        completed = set()
        in_progress = set()
        future = set()
        status_details = {}
        
        for node in G.nodes():
            if node not in ['START', 'END']:
                es = G.nodes[node].get('ES', 0)
                ef = G.nodes[node].get('EF', 0)
                duration = G.nodes[node].get('duration', 1)
                
                # Determine activity status
                if ef <= current_time:
                    completed.add(node)
                    status = 'completed'
                    progress = 1.0
                elif es <= current_time < ef:
                    in_progress.add(node)
                    status = 'in_progress' 
                    progress = (current_time - es) / duration if duration > 0 else 0
                else:
                    future.add(node)
                    status = 'future'
                    progress = 0.0
                
                # Store detailed status information
                status_details[node] = {
                    'status': status,
                    'es': es,
                    'ef': ef,
                    'duration': duration,
                    'progress': min(1.0, max(0.0, progress)),
                    'time_remaining': max(0, ef - current_time),
                    'can_be_crashed': (status in ['in_progress', 'future'] and 
                                     G.nodes[node].get('duration', 1) > G.nodes[node].get('min_duration', 1))
                }
        
        return {
            'completed': completed,
            'in_progress': in_progress,
            'future': future,
            'status_details': status_details,
            'summary': {
                'total_activities': len(status_details),
                'completed_count': len(completed),
                'in_progress_count': len(in_progress),
                'future_count': len(future)
            }
        }

    def evaluate_crash_candidates(self, G, resource_limit, priority_rule, current_time, critical_activities):
        """
        Evaluate each crashable activity using dynamic RCPS impact assessment.
        
        This method implements the core improvement: evaluating crash decisions based on
        actual RCPS impact rather than static cost assumptions.
        """
        candidates = []
        
        # Get current project duration for comparison
        current_duration = max([G.nodes[node]['EF'] for node in G.nodes() if 'EF' in G.nodes[node]])
        
        # Get activity status for eligibility checking
        status_data = self.analyze_activity_status(G, current_time)
        
        for activity in critical_activities:
            # Check basic crash eligibility
            eligibility = self._check_crash_eligibility(G, activity, current_time, status_data)
            
            if not eligibility['eligible']:
                continue
            
            try:
                # Create temporary crashed graph
                temp_G = G.copy()
                temp_G.nodes[activity]['duration'] = max(
                    eligibility['min_duration'],
                    eligibility['current_duration'] - 1
                )
                
                # Recalculate CPM for temporary graph
                temp_G = self._recalculate_cpm(temp_G)
                
                # Generate RCPS schedule for crashed scenario
                temp_schedule = self.generate_rcps_schedule_for_graph(
                    temp_G, resource_limit, priority_rule
                )
                
                if temp_schedule['schedule_feasible']:
                    new_duration = temp_schedule['project_duration']
                    duration_reduction = current_duration - new_duration
                    
                    if duration_reduction > 0:
                        cost_effectiveness = eligibility['crash_cost'] / duration_reduction
                        
                        candidates.append({
                            'activity_id': activity,
                            'crash_cost': eligibility['crash_cost'],
                            'duration_reduction': duration_reduction,
                            'new_project_duration': new_duration,
                            'cost_effectiveness': cost_effectiveness,
                            'current_duration': eligibility['current_duration'],
                            'min_duration': eligibility['min_duration'],
                            'es': eligibility['es'],
                            'ef': eligibility['ef'],
                            'is_in_progress': eligibility['is_in_progress'],
                            'schedule_data': temp_schedule,
                            'feasible': True
                        })
            
            except Exception as e:
                print(f"Error evaluating crash candidate {activity}: {e}")
                continue
        
        # Sort by cost effectiveness (best first)
        candidates.sort(key=lambda x: x['cost_effectiveness'])
        
        return candidates
    
    def _check_crash_eligibility(self, G, activity, current_time, status_data):
        """Check if activity is eligible for crashing at current time."""
        node_data = G.nodes[activity]
        
        current_dur = node_data.get('duration', 1)
        min_dur = node_data.get('min_duration', 1)
        crash_cost = node_data.get('crash_cost', 100)
        es = node_data.get('ES', 0)
        ef = node_data.get('EF', 0)
        
        activity_status = status_data['status_details'].get(activity, {})
        status = activity_status.get('status', 'unknown')
        
        # Enhanced eligibility logic
        not_finished = (status in ['in_progress', 'future'])
        has_crash_potential = (current_dur > min_dur)
        has_crash_cost = (crash_cost > 0)
        is_critical = (node_data.get('float', 0) == 0)
        
        eligible = (not_finished and has_crash_potential and has_crash_cost and is_critical)
        
        return {
            'eligible': eligible,
            'crash_cost': crash_cost,
            'current_duration': current_dur,
            'min_duration': min_dur,
            'es': es,
            'ef': ef,
            'is_in_progress': (status == 'in_progress'),
            'status': status,
            'not_finished': not_finished,
            'has_crash_potential': has_crash_potential,
            'has_crash_cost': has_crash_cost,
            'is_critical': is_critical
        }
    
    def _recalculate_cpm(self, G):
        """Recalculate CPM for the given graph."""
        # Use existing network builder if available
        network_builder = getattr(self.base_analyzer, 'network_builder', None)
        if network_builder:
            G = network_builder.forward_pass(G)
            G = network_builder.backward_pass(G)
            G = network_builder.calculate_float(G)
        else:
            # Fallback: use basic CPM calculations
            print("[WARNING] No network_builder found, using basic CPM fallback")
            # For now, preserve existing values
            pass
        
        return G
