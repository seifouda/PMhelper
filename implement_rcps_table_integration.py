#!/usr/bin/env python3
"""
RCPS Table Data Integration - Option 1 Implementation

Creates an analyzer directly from RCPS table data instead of using CPM data.
This ensures RCPS crashing uses the resource-constrained times and durations.
"""

def implement_rcps_table_integration():
    """Implement RCPS table data integration in RCPS crashing tab"""
    
    print("🚀 IMPLEMENTING OPTION 1: DIRECT RCPS TABLE DATA CONVERSION")
    print("=" * 80)
    
    # The implementation involves modifying the RCPS crashing tab to:
    # 1. Get RCPS table data instead of CPM analyzer
    # 2. Create a new analyzer from RCPS table data  
    # 3. Use this analyzer for crashing

    rcps_integration_code = '''
def run_crashing_with_rcps_data(self):
    """
    RCPS TABLE INTEGRATION: Use RCPS table data for crashing
    This creates an analyzer from RCPS processed data instead of original CPM data
    """
    try:
        # 1. Get input parameters (same as before)
        try:
            target_duration = int(round(float(self.target_duration_var.get())))
        except ValueError:
            messagebox.showerror("Input Error", "Target Duration must be an integer.")
            return

        try:
            strategy = CrashingStrategy(self.strategy_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Invalid strategy selected.")
            return

        try:
            objective = OptimizationObjective(self.objective_var.get())
        except Exception:
            messagebox.showerror("Input Error", "Invalid objective selected.")
            return

        # Get budget parameters
        max_budget = self.budget_var.get()
        try:
            max_budget = int(round(float(max_budget))) if max_budget else None
        except ValueError:
            messagebox.showerror("Input Error", "Max Budget must be an integer or blank.")
            return

        max_crash_cost = self.max_crash_cost_var.get()
        try:
            max_crash_cost = int(round(float(max_crash_cost))) if max_crash_cost else None
        except ValueError:
            messagebox.showerror("Input Error", "Max Crashing Cost must be an integer or blank.")
            return

        max_normal_cost = self.max_normal_cost_var.get()
        try:
            max_normal_cost = int(round(float(max_normal_cost))) if max_normal_cost else None
        except ValueError:
            messagebox.showerror("Input Error", "Max Normal Cost must be an integer or blank.")
            return
        
        # 2. CRITICAL: Get RCPS table data instead of CPM analyzer
        rcps_table_data = self.get_rcps_table_data()
        if rcps_table_data is None:
            messagebox.showerror("Data Error", "No RCPS table data available. Run RCPS analysis first.")
            return
            
        print(f"[RCPS TABLE] Got RCPS table data with shape: {rcps_table_data.shape}")
        
        # 3. Create analyzer from RCPS table data
        rcps_analyzer = self.create_analyzer_from_rcps_table(rcps_table_data)
        if rcps_analyzer is None:
            messagebox.showerror("Data Error", "Failed to create analyzer from RCPS data.")
            return
            
        print(f"[RCPS TABLE] Created analyzer from RCPS data: {type(rcps_analyzer)}")
        
        # 4. Validate RCPS project duration
        if hasattr(rcps_analyzer, 'G') and rcps_analyzer.G is not None:
            try:
                # Use RCPS processed durations instead of original CPM
                ef_values = [rcps_analyzer.G.nodes[node].get('EF', 0) for node in rcps_analyzer.G.nodes()]
                if not any(ef > 0 for ef in ef_values):
                    messagebox.showwarning(
                        "Analysis Required", 
                        "RCPS analysis data appears invalid. Please run RCPS analysis first."
                    )
                    return
                
                rcps_project_duration = max(ef_values) if ef_values else 0
                
                print(f"[RCPS TABLE] RCPS project duration: {rcps_project_duration}")
                
                if target_duration >= rcps_project_duration:
                    messagebox.showwarning(
                        "Invalid Target Duration", 
                        f"Target duration ({target_duration}) must be less than the RCPS project duration ({rcps_project_duration}).\\n\\n"
                        f"Note: This is the resource-constrained duration, not the original CPM duration."
                    )
                    return
            except Exception as e:
                messagebox.showwarning("Duration Check", f"Could not validate target duration: {e}")
        else:
            messagebox.showwarning(
                "Analysis Required", 
                "RCPS analyzer is invalid. Please run RCPS analysis first."
            )
            return

        # 5. Use normal ProjectCrashing engine with RCPS analyzer
        from .project_crashing_core import ProjectCrashing
        
        crashing_engine = ProjectCrashing(rcps_analyzer)  # Now uses RCPS data!
        
        print(f"[RCPS TABLE] Using ProjectCrashing engine with RCPS analyzer")
        
        result = crashing_engine.run(
            target_duration=target_duration,
            strategy=strategy,
            objective=objective,
            max_budget=max_budget,
            max_crash_cost=max_crash_cost,
            max_normal_cost=max_normal_cost,
            max_iterations=300
        )

        # 6. Display results and visualization
        self.display_results(result)
        self.update_visualization(result)
        
        print(f"[RCPS TABLE] RCPS crashing with table data completed successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"RCPS Crashing with table data failed: {str(e)}")
        import traceback
        traceback.print_exc()

def get_rcps_table_data(self):
    """Get RCPS table data from RCPS tab"""
    try:
        # Access RCPS tab through app
        if hasattr(self.app, 'rcps_tab') and self.app.rcps_tab:
            rcps_tab = self.app.rcps_tab
            if hasattr(rcps_tab, 'rcps_table_data') and rcps_tab.rcps_table_data is not None:
                return rcps_tab.rcps_table_data.copy()  # Return copy to avoid modifications
        
        # Fallback: try to get through tab reference
        if hasattr(self.tab, 'rcps_tab') and self.tab.rcps_tab:
            rcps_tab = self.tab.rcps_tab
            if hasattr(rcps_tab, 'rcps_table_data') and rcps_tab.rcps_table_data is not None:
                return rcps_tab.rcps_table_data.copy()
                
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get RCPS table data: {e}")
        return None

def create_analyzer_from_rcps_table(self, rcps_table):
    """Create analyzer from RCPS table data"""
    try:
        # Import the CPM analyzer to create compatible structure
        from pmhelper.core.cpm_analyzer import CPMAnalyzer
        
        # Create new analyzer instance
        analyzer = CPMAnalyzer()
        
        # Filter out resource rows and extract activities
        activity_rows = rcps_table[~rcps_table['id'].isin(['RA', 'RS'])]
        
        # Convert RCPS table to activities list
        activities = []
        for _, row in activity_rows.iterrows():
            activity = {
                'id': row.get('id'),
                'name': row.get('name', f"Activity {row.get('id')}"),
                'duration': row.get('duration'),
                'early_start': row.get('early_start'),
                'early_finish': row.get('early_finish', row.get('early_start', 0) + row.get('duration', 0)),
                'late_start': row.get('late_start'),
                'late_finish': row.get('late_finish'),
                'actual_start': row.get('actual_start'),
                'float': row.get('float', 0),
                'critical': row.get('critical', row.get('float', 0) == 0),
                'predecessors': row.get('predecessors', ''),
                'crash_cost': row.get('crash_cost', 0),
                'min_duration': row.get('min_duration', row.get('duration')),
                'normal_cost': row.get('normal_cost', 0),
                'resource': row.get('resource', 1)
            }
            activities.append(activity)
        
        # Set activities in analyzer
        analyzer.activities = activities
        
        # Create NetworkX graph from RCPS data
        import networkx as nx
        G = nx.DiGraph()
        
        # Add nodes with RCPS processed attributes
        for activity in activities:
            G.add_node(activity['id'], **activity)
        
        # Add edges based on predecessors
        for activity in activities:
            predecessors = activity.get('predecessors', '')
            if predecessors:
                pred_list = [p.strip() for p in predecessors.split(',') if p.strip()]
                for pred in pred_list:
                    if pred in G.nodes():
                        G.add_edge(pred, activity['id'])
        
        # Set graph in analyzer
        analyzer.G = G
        
        # Set project duration from RCPS data
        if activities:
            analyzer.project_duration = max(act.get('late_finish', act.get('early_finish', 0)) for act in activities)
        
        print(f"[RCPS TABLE] Created analyzer with {len(activities)} activities, duration {analyzer.project_duration}")
        
        return analyzer
        
    except Exception as e:
        print(f"[ERROR] Failed to create analyzer from RCPS table: {e}")
        import traceback
        traceback.print_exc()
        return None
'''
    
    print("📋 IMPLEMENTATION COMPONENTS:")
    print("1. ✅ get_rcps_table_data() - Gets RCPS processed table")
    print("2. ✅ create_analyzer_from_rcps_table() - Converts table to analyzer")
    print("3. ✅ run_crashing_with_rcps_data() - Main integration method")
    print("4. ✅ Uses RCPS durations and times instead of CPM")
    
    print("\n🎯 BENEFITS:")
    print("• Uses actual RCPS processed ES, EF, LS, LF times")
    print("• Includes resource-constrained project duration")
    print("• Preserves all RCPS scheduling results")
    print("• Compatible with existing crashing engine")
    print("• Maintains crash cost and min_duration data")
    
    return rcps_integration_code

if __name__ == "__main__":
    code = implement_rcps_table_integration()
    print("\n" + "="*80)
    print("IMPLEMENTATION CODE:")
    print("="*80)
    print(code)
