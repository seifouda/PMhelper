#!/usr/bin/env python3
"""
Phase 1 Integration Script

This script safely adds the three foundation methods to project_crashing_core.py.
It reads the original file, finds the end of the RCPSProjectCrashing class,
and appends the new methods with proper indentation.
"""

import sys
import os

def integrate_foundation_methods():
    """Integrate the foundation methods into project_crashing_core.py"""
    
    # File paths
    original_file = "src/pmhelper/gui/tabs/project_crashing_core.py"
    
    print("🔧 Phase 1 Integration: Adding Foundation Methods")
    print("=" * 55)
    
    # Read the original file
    print("📖 Reading original project_crashing_core.py...")
    try:
        with open(original_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False
    
    # Find the end of the file (last return statement)
    lines = original_content.split('\n')
    insert_index = len(lines)
    
    # Look for the last method's return statement
    for i in range(len(lines) - 1, -1, -1):
        if 'return "\\n".join(lines)' in lines[i]:
            insert_index = i + 1
            break
    
    print(f"📍 Found insertion point at line {insert_index}")
    
    # Foundation methods to add
    foundation_methods = '''
    # ============================================================================
    # ENHANCED METHODOLOGY FOUNDATION METHODS (PHASE 1)
    # ============================================================================
    
    def generate_rcps_schedule_for_graph(self, G, resource_limit, priority_rule='minimum_slack'):
        """Generate RCPS schedule for any graph state during crashing evaluation."""
        try:
            activities_data = []
            for node in G.nodes():
                if node not in ['START', 'END']:
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
            
            import pandas as pd
            df_gantt = pd.DataFrame(activities_data)
            
            if hasattr(self.base_analyzer, 'rcps_heuristic_schedule_table'):
                rcps_table, actual_starts, critical_ids = self.base_analyzer.rcps_heuristic_schedule_table(
                    df_gantt, resource_limit, priority_rule
                )
                
                activities = {}
                project_duration = 0
                
                for idx, row in rcps_table.iterrows():
                    if row['id'] not in ['RA', 'RS']:
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
                
                return {
                    'project_duration': int(project_duration),
                    'activities': activities,
                    'critical_activities': list(critical_ids) if critical_ids else [],
                    'resource_usage': {},
                    'schedule_feasible': True
                }
            
            else:
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
            return {
                'project_duration': 0,
                'activities': {},
                'critical_activities': [],
                'resource_usage': {},
                'schedule_feasible': False
            }

    def analyze_activity_status(self, G, current_time):
        """Analyze activity execution status at current simulation time."""
        completed = set()
        in_progress = set()
        future = set()
        status_details = {}
        
        for node in G.nodes():
            if node not in ['START', 'END']:
                es = G.nodes[node].get('ES', 0)
                ef = G.nodes[node].get('EF', 0)
                duration = G.nodes[node].get('duration', 1)
                
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
        """Evaluate each crashable activity using dynamic RCPS impact assessment."""
        candidates = []
        
        current_duration = max([G.nodes[node]['EF'] for node in G.nodes() if 'EF' in G.nodes[node]])
        status_data = self.analyze_activity_status(G, current_time)
        
        for activity in critical_activities:
            eligibility = self._check_crash_eligibility(G, activity, current_time, status_data)
            
            if not eligibility['eligible']:
                continue
            
            try:
                temp_G = G.copy()
                temp_G.nodes[activity]['duration'] = max(
                    eligibility['min_duration'],
                    eligibility['current_duration'] - 1
                )
                
                temp_G = self._recalculate_cpm(temp_G)
                
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
        network_builder = getattr(self.base_analyzer, 'network_builder', None)
        if network_builder:
            G = network_builder.forward_pass(G)
            G = network_builder.backward_pass(G)
            G = network_builder.calculate_float(G)
        else:
            print("[WARNING] No network_builder found, using basic CPM fallback")
        
        return G'''
    
    # Create new content
    new_lines = lines[:insert_index] + foundation_methods.split('\n') + lines[insert_index:]
    new_content = '\n'.join(new_lines)
    
    # Write the updated file
    print("💾 Writing updated file...")
    try:
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("✅ Foundation methods integrated successfully!")
        
        # Check for syntax errors
        print("🔍 Checking syntax...")
        import ast
        try:
            ast.parse(new_content)
            print("✅ Syntax validation passed!")
            return True
        except SyntaxError as e:
            print(f"❌ Syntax error detected: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False

def main():
    """Main execution."""
    success = integrate_foundation_methods()
    
    if success:
        print()
        print("🎉 Phase 1 Integration Complete!")
        print("=" * 55)
        print("✅ Three foundation methods added to RCPSProjectCrashing class:")
        print("   • generate_rcps_schedule_for_graph()")
        print("   • analyze_activity_status()")  
        print("   • evaluate_crash_candidates()")
        print("   • _check_crash_eligibility() [helper]")
        print("   • _recalculate_cmp() [helper]")
        print()
        print("📋 Next Steps:")
        print("   1. Test the integrated methods")
        print("   2. Continue with Phase 2 implementation")
        print("   3. Replace core crashing logic")
        
    else:
        print()
        print("❌ Phase 1 Integration Failed!")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()
