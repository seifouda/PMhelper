
    def evaluate_crash_candidates(self, G, resource_limit, priority_rule, current_time, critical_activities):
        """
        Evaluate each crashable activity using dynamic RCPS impact assessment.
        
        This method implements the core improvement: evaluating crash decisions based on
        actual RCPS impact rather than static cost assumptions.
        
        Args:
            G (networkx.DiGraph): Current project graph
            resource_limit (int): Resource constraint
            priority_rule (str): RCPS scheduling rule
            current_time (float): Current simulation time
            critical_activities (list): Activities on critical path
        
        Returns:
            list: Ranked crash candidates with RCPS-validated impact data
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
    
    def _recalculate_cmp(self, G):
        """Recalculate CPM for the given graph."""
        # Use existing network builder if available
        network_builder = getattr(self.base_analyzer, 'network_builder', None)
        if network_builder:
            G = network_builder.forward_pass(G)
            G = network_builder.backward_pass(G)
            G = network_builder.calculate_float(G)
        else:
            # Fallback to basic CPM calculations
            # This would need to be implemented based on existing CPM logic
            pass
        
        return G
    