#!/usr/bin/env python3
"""
QUICK-START IMPLEMENTATION SCRIPT
Phase 1: Foundation Methods Implementation
==========================================

This script provides a step-by-step implementation guide for Phase 1 of the 
enhanced RCPS crashing methodology. Follow the steps in order to build the
foundation methods required for the improved approach.

Run this script to generate starter templates and validate the current state.
"""

import os
import sys
import time

def check_environment():
    """Check if the development environment is ready."""
    print("🔍 CHECKING DEVELOPMENT ENVIRONMENT")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check required directories
    required_dirs = [
        "src/pmhelper/gui/tabs",
        "src/pmhelper/core"
    ]
    
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"✅ Directory exists: {dir_path}")
        else:
            print(f"❌ Directory missing: {dir_path}")
    
    # Check required files
    required_files = [
        "src/pmhelper/gui/tabs/project_crashing_core.py",
        "src/pmhelper/gui/tabs/rcps_crashing_tab_gui.py",
        "src/pmhelper/core/rcps_analyzer.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ File exists: {file_path}")
        else:
            print(f"❌ File missing: {file_path}")
    
    print("\n" + "=" * 50)
    return True

def generate_phase1_templates():
    """Generate template code for Phase 1 implementation."""
    print("📝 GENERATING PHASE 1 IMPLEMENTATION TEMPLATES")
    print("=" * 50)
    
    # Template 1: generate_rcps_schedule_for_graph method
    template1 = '''
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
    '''
    
    # Template 2: analyze_activity_status method
    template2 = '''
    def analyze_activity_status(self, G, current_time):
        """
        Analyze activity execution status at current simulation time.
        
        This method provides sophisticated activity status tracking that distinguishes
        between completed, in-progress, and future activities based on current simulation time.
        
        Args:
            G (networkx.DiGraph): Project network graph
            current_time (float): Current simulation time
        
        Returns:
            dict: {
                'completed': set,       # Activities that have finished (EF <= current_time)
                'in_progress': set,     # Activities currently executing (ES <= current_time < EF)
                'future': set,          # Activities not yet started (ES > current_time)
                'status_details': dict  # Detailed status information per activity
            }
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
    '''
    
    # Template 3: evaluate_crash_candidates method
    template3 = '''
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
    '''
    
    print("📄 Template 1: generate_rcps_schedule_for_graph")
    print("   - Core RCPS integration method")
    print("   - Converts NetworkX to RCPS schedule")
    print("   - Returns comprehensive schedule data")
    
    print("\n📄 Template 2: analyze_activity_status") 
    print("   - Sophisticated activity status tracking")
    print("   - Distinguishes completed/in-progress/future")
    print("   - Provides detailed status information")
    
    print("\n📄 Template 3: evaluate_crash_candidates")
    print("   - Dynamic RCPS-aware cost evaluation")
    print("   - Tests actual project impact")
    print("   - Returns ranked crash candidates")
    
    # Save templates to files
    os.makedirs("templates", exist_ok=True)
    
    with open("templates/phase1_method1_rcps_schedule.py", "w") as f:
        f.write(template1)
    
    with open("templates/phase1_method2_activity_status.py", "w") as f:
        f.write(template2)
    
    with open("templates/phase1_method3_crash_evaluation.py", "w") as f:
        f.write(template3)
    
    print(f"\n✅ Templates saved to templates/ directory")
    print("=" * 50)

def create_implementation_checklist():
    """Create implementation checklist for Phase 1."""
    checklist = '''
PHASE 1 IMPLEMENTATION CHECKLIST
================================

□ STEP 1: Backup Current Implementation (15 mins)
  □ Copy project_crashing_core.py to project_crashing_core_backup.py
  □ Create git branch for enhanced implementation
  □ Document current method signatures

□ STEP 2: Add generate_rcps_schedule_for_graph Method (2 hours)
  □ Copy template code to RCPSProjectCrashing class
  □ Integrate with existing RCPSAnalyzer interface
  □ Test with simple graph scenarios
  □ Validate schedule data format
  □ Handle edge cases (empty graph, invalid data)

□ STEP 3: Add analyze_activity_status Method (1.5 hours)
  □ Copy template code to RCPSProjectCrashing class
  □ Test status detection with sample data
  □ Validate progress calculations
  □ Test edge cases (zero duration, negative times)
  □ Verify status transition logic

□ STEP 4: Add evaluate_crash_candidates Method (1.5 hours)
  □ Copy template code to RCPSProjectCrashing class
  □ Implement _check_crash_eligibility helper
  □ Implement _recalculate_cpm helper  
  □ Test candidate evaluation logic
  □ Validate cost-effectiveness calculations
  □ Test with various resource constraints

□ STEP 5: Basic Integration Testing (30 mins)
  □ Test all three methods together
  □ Verify method interfaces work correctly
  □ Check for import/dependency issues
  □ Validate return data formats
  □ Test error handling

□ STEP 6: Create Phase 1 Validation Script (30 mins)
  □ Create test script for Phase 1 methods
  □ Test with known project data
  □ Validate against expected results
  □ Document any issues found

ESTIMATED TOTAL TIME: 5-6 hours

COMPLETION CRITERIA:
✅ All three foundation methods implemented
✅ Basic functionality tests passing
✅ No critical errors in method integration
✅ Ready for Phase 2 implementation

NEXT PHASE: Replace main crash_project() method with time-based simulation
'''
    
    with open("PHASE1_CHECKLIST.md", "w") as f:
        f.write(checklist)
    
    print("📋 IMPLEMENTATION CHECKLIST CREATED")
    print("   - Saved as PHASE1_CHECKLIST.md")
    print("   - Follow step-by-step for Phase 1")
    print("   - Estimated time: 5-6 hours")

def main():
    """Main execution function."""
    print("🚀 ENHANCED RCPS CRASHING - QUICK START")
    print("=" * 50)
    print("Phase 1: Foundation Methods Implementation")
    print("Time Estimate: 4-5 hours")
    print("\n")
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed. Please fix issues before continuing.")
        return
    
    print("\n")
    
    # Generate templates
    generate_phase1_templates()
    
    print("\n")
    
    # Create checklist
    create_implementation_checklist()
    
    print("\n" + "=" * 50)
    print("🎯 NEXT STEPS:")
    print("1. Review generated templates in templates/ directory")
    print("2. Follow PHASE1_CHECKLIST.md step by step")
    print("3. Implement foundation methods in project_crashing_core.py")
    print("4. Test each method individually before proceeding")
    print("5. Run Phase 1 validation before moving to Phase 2")
    print("\n📚 For detailed guidance, see FULL_EXECUTION_PLAN.md")
    print("=" * 50)

if __name__ == "__main__":
    main()
