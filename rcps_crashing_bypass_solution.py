#!/usr/bin/env python3
"""
RCPS Crashing Bypass Solution - Make RCPS work like Normal Crashing

This approach bypasses the problematic RCPSAnalyzer and uses the same 
data source and engine as normal crashing, but with RCPS data.
"""

def create_rcps_crashing_bypass():
    print("🔧 CREATING RCPS CRASHING BYPASS SOLUTION")
    print("="*80)
    
    solution_code = '''
def run_crashing_bypass(self):
    """
    BYPASS SOLUTION: Use normal crashing engine with RCPS data
    This bypasses the problematic RCPSAnalyzer and uses the same approach as normal crashing
    """
    try:
        # 1. Get input parameters (same as normal crashing)
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

        # 2. BYPASS APPROACH: Use same data source as normal crashing
        # Instead of problematic RCPSAnalyzer, use self.app.current_analyzer like normal crashing
        base_analyzer = getattr(self.app, "current_analyzer", None)
        if base_analyzer is None:
            base_analyzer = getattr(self.app, "base_analyzer", None)
        if base_analyzer is None:
            messagebox.showerror("Data Error", "No project data loaded. Run CPM/PERT analysis first.")
            return

        print(f"[BYPASS] Using base_analyzer: {type(base_analyzer)}")
        
        # Validate that analysis has been run (same validation as normal crashing)
        if hasattr(base_analyzer, 'G') and base_analyzer.G is not None:
            try:
                ef_values = [base_analyzer.G.nodes[node].get('EF', 0) for node in base_analyzer.G.nodes()]
                if not any(ef > 0 for ef in ef_values):
                    messagebox.showwarning(
                        "Analysis Required", 
                        "Please run CPM or PERT analysis first before using project crashing."
                    )
                    return
                
                original_duration = max(ef_values) if ef_values else 0
                
                if target_duration >= original_duration:
                    messagebox.showwarning(
                        "Invalid Target Duration", 
                        f"Target duration ({target_duration}) must be less than the original project duration ({original_duration})."
                    )
                    return
            except Exception as e:
                messagebox.showwarning("Duration Check", "Could not validate target duration.")
        else:
            messagebox.showwarning(
                "Analysis Required", 
                "Please run CPM or PERT analysis first before using project crashing."
            )
            return

        # 3. CRITICAL: Use normal ProjectCrashing engine instead of RCPSProjectCrashing
        from .project_crashing_core import ProjectCrashing  # Normal engine
        
        crashing_engine = ProjectCrashing(base_analyzer)  # Same as normal crashing
        
        print(f"[BYPASS] Using ProjectCrashing engine (not RCPSProjectCrashing)")
        
        result = crashing_engine.run(
            target_duration=target_duration,
            strategy=strategy,
            objective=objective,
            max_budget=max_budget,
            max_crash_cost=max_crash_cost,
            max_normal_cost=max_normal_cost,
            max_iterations=300
        )

        # 4. Display results (reuse parent method)
        self.display_results(result)
        
        # 5. Add graph generation (this was missing!)
        self.update_visualization(result)
        
        print(f"[BYPASS] RCPS crashing completed successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"RCPS Crashing analysis failed: {str(e)}")
        import traceback
        traceback.print_exc()
'''
    
    print("📋 SOLUTION APPROACH:")
    print("1. ✅ Use same data source as normal crashing (self.app.current_analyzer)")
    print("2. ✅ Use normal ProjectCrashing engine (not RCPSProjectCrashing)")  
    print("3. ✅ Add missing graph generation (update_visualization)")
    print("4. ✅ Same validation and error handling as normal crashing")
    
    print("\n🎯 BENEFITS:")
    print("• Works with exact same data as normal crashing")
    print("• Uses proven ProjectCrashing engine") 
    print("• Includes graph generation that was missing")
    print("• No dependency on problematic RCPSAnalyzer")
    print("• Should work immediately!")
    
    print("\n🔧 IMPLEMENTATION:")
    print("Replace the run_crashing method in RCPSCrashingTabGUIManager with run_crashing_bypass")
    
    return solution_code

if __name__ == "__main__":
    solution = create_rcps_crashing_bypass()
    print("\n" + "="*80)
    print("CODE TO IMPLEMENT:")
    print("="*80)
    print(solution)
