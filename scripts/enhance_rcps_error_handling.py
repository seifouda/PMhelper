#!/usr/bin/env python3
"""
RCPS Error Handling Enhancement Script
Adds comprehensive error handling to RCPS tab functionality
"""

from pathlib import Path
import re

class RCPSErrorHandlingEnhancer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.rcps_file = self.project_root / "src/pmhelper/gui/tabs/rcps_tab.py"
        
    def add_input_validation(self):
        """Add comprehensive input validation method"""
        validation_method = '''
    def validate_rcps_inputs(self, df_gantt, resource_limit, priority_rule):
        """
        Comprehensive input validation for RCPS analysis
        
        Args:
            df_gantt: Project data DataFrame
            resource_limit: Maximum available resources
            priority_rule: Scheduling priority rule
            
        Raises:
            ValueError: If any input is invalid
        """
        errors = []
        
        # Data validation
        if df_gantt is None:
            errors.append("No project data available. Please run CPM or PERT analysis first.")
        elif df_gantt.empty:
            errors.append("Project data is empty. Please load valid project data.")
        else:
            # Check required columns
            required_columns = ['id', 'duration', 'resource', 'early_start', 'late_finish', 'float']
            missing_columns = [col for col in required_columns if col not in df_gantt.columns]
            if missing_columns:
                errors.append(f"Missing required data columns: {', '.join(missing_columns)}")
            
            # Check for valid data types
            try:
                pd.to_numeric(df_gantt['duration'], errors='coerce')
                pd.to_numeric(df_gantt['resource'], errors='coerce')
            except Exception:
                errors.append("Invalid data types in duration or resource columns")
        
        # Resource validation  
        if not isinstance(resource_limit, (int, float)) or resource_limit <= 0:
            errors.append("Resource limit must be a positive number")
        elif df_gantt is not None and 'resource' in df_gantt.columns:
            try:
                max_resource = pd.to_numeric(df_gantt['resource'], errors='coerce').max()
                if not pd.isna(max_resource) and resource_limit < max_resource:
                    errors.append(f"Resource limit ({resource_limit}) cannot be less than maximum single activity resource requirement ({max_resource})")
            except Exception:
                pass  # Skip validation if resource column has issues
                
        # Priority rule validation
        valid_rules = ['minimum_slack', 'shortest_duration', 'earliest_start']
        if priority_rule not in valid_rules:
            errors.append(f"Invalid priority rule '{priority_rule}'. Valid options: {', '.join(valid_rules)}")
        
        if errors:
            raise ValueError("\\n".join(errors))
'''
        return validation_method
    
    def add_progress_dialog(self):
        """Add progress dialog implementation"""
        progress_code = '''
    def create_progress_dialog(self):
        """Create a progress dialog for long-running RCPS operations"""
        import tkinter as tk
        from tkinter import ttk
        
        class ProgressDialog:
            def __init__(self, parent):
                self.window = tk.Toplevel(parent)
                self.window.title("RCPS Analysis Progress")
                self.window.geometry("400x150")
                self.window.resizable(False, False)
                self.window.grab_set()  # Make it modal
                
                # Center the dialog
                self.window.transient(parent)
                self.window.geometry("+%d+%d" % (
                    parent.winfo_rootx() + 50,
                    parent.winfo_rooty() + 50
                ))
                
                # Create widgets
                main_frame = ttk.Frame(self.window, padding="20")
                main_frame.pack(fill=tk.BOTH, expand=True)
                
                self.status_label = ttk.Label(main_frame, text="Initializing RCPS analysis...")
                self.status_label.pack(pady=(0, 10))
                
                self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
                self.progress_bar.pack(fill=tk.X, pady=(0, 10))
                self.progress_bar.start()
                
                self.detail_label = ttk.Label(main_frame, text="", foreground="gray")
                self.detail_label.pack()
                
            def update_status(self, message, detail=""):
                """Update the progress dialog status"""
                self.status_label.config(text=message)
                if detail:
                    self.detail_label.config(text=detail)
                self.window.update()
                
            def close(self):
                """Close the progress dialog"""
                self.progress_bar.stop()
                self.window.destroy()
        
        return ProgressDialog(self.rcps_frame)
'''
        return progress_code
    
    def add_enhanced_run_rcps(self):
        """Create enhanced run_rcps method with error handling"""
        enhanced_method = '''
    def run_rcps_with_error_handling(self):
        """Enhanced RCPS execution with comprehensive error handling and progress indication"""
        progress_dialog = None
        
        try:
            # Create progress dialog
            progress_dialog = self.create_progress_dialog()
            
            # Step 1: Get inputs
            progress_dialog.update_status("Validating inputs...", "Checking resource limits and priority rules")
            resource_limit = self.resource_limit_var.get()
            priority_rule = self.priority_rule_var.get()
            df_gantt = self.main_window.current_data
            
            # Step 2: Validate inputs
            self.validate_rcps_inputs(df_gantt, resource_limit, priority_rule)
            
            # Step 3: Prepare analyzers
            progress_dialog.update_status("Preparing analysis engines...", "Selecting appropriate analyzer (CPM/PERT)")
            analysis_mode = getattr(self.main_window, 'analysis_mode', None)
            if analysis_mode == 'probabilistic':
                analyzer = self.main_window.pert_analyzer
            else:
                analyzer = self.main_window.cmp_analyzer
            
            if analyzer is None:
                raise ValueError("Analysis engine not available. Please run CPM or PERT analysis first.")
            
            # Step 4: Generate schedules
            progress_dialog.update_status("Generating schedules...", "Computing CPM baseline and RCPS optimization")
            
            # Generate CPM and RCPS tables
            cmp_table, _, _ = analyzer.build_cmp_schedule_table(df_gantt, resource_limit)
            rcps_table, _, _ = analyzer.rcps_heuristic_schedule_table(df_gantt, resource_limit, priority_rule=priority_rule)
            
            # Step 5: Process timeline data
            progress_dialog.update_status("Processing timeline data...", "Calculating resource utilization patterns")
            
            timeline_cols = [col for col in cmp_table.columns if isinstance(col, int)]
            
            # Fill timeline columns with resource usage
            self._fill_timeline_data(cmp_table, timeline_cols, is_rcps=False)
            self._fill_timeline_data(rcps_table, timeline_cols, is_rcps=True)
            
            # Step 6: Update display
            progress_dialog.update_status("Updating display...", "Rendering tables and charts")
            
            # Clear previous content
            for widget in self.tables_frame.winfo_children():
                widget.destroy()
            
            # Align table columns
            rcps_columns = list(rcps_table.columns)
            cmp_columns = [col for col in rcps_columns if col != 'actual_start']
            cmp_table_aligned = cmp_table.reindex(columns=cmp_columns, fill_value='')
            
            # Display hybrid layout
            self.display_hybrid_schedule_view(self.tables_frame, cmp_table_aligned, rcps_table, df_gantt)
            
            progress_dialog.update_status("Analysis complete!", "RCPS scheduling successfully generated")
            
        except ValueError as ve:
            # User input errors - show user-friendly message
            if progress_dialog:
                progress_dialog.close()
            messagebox.showerror("Input Error", str(ve))
            
        except MemoryError:
            # Memory issues with large projects
            if progress_dialog:
                progress_dialog.close()
            messagebox.showerror("Memory Error", 
                "Project too large for available memory. Try reducing the project size or increasing system memory.")
            
        except Exception as e:
            # Unexpected system errors
            if progress_dialog:
                progress_dialog.close()
            
            import traceback
            import logging
            
            # Log detailed error for debugging
            logging.error(f"RCPS Analysis Error: {str(e)}", exc_info=True)
            print(f"RCPS Error Details:\\n{traceback.format_exc()}")
            
            # Show user-friendly error message
            messagebox.showerror("Analysis Error", 
                f"RCPS analysis encountered an unexpected error.\\n\\n"
                f"Error: {str(e)[:100]}{'...' if len(str(e)) > 100 else ''}\\n\\n"
                f"Please check your project data and try again. "
                f"If the problem persists, contact support.")
            
            # Attempt to show fallback display
            try:
                self.show_fallback_display()
            except Exception:
                pass  # If fallback also fails, just leave empty
                
        finally:
            # Ensure progress dialog is closed
            if progress_dialog:
                progress_dialog.close()
    
    def _fill_timeline_data(self, table, timeline_cols, is_rcps=False):
        """Helper method to fill timeline columns with resource usage data"""
        for idx, row in table.iterrows():
            if row['id'] in ['RA', 'RS']:
                continue
            try:
                if is_rcps and 'actual_start' in row and row['actual_start'] != '':
                    start = int(row['actual_start'])
                else:
                    start = int(row['early_start'])
                    
                dur = int(row['duration'])
                res = int(row['resource'])
                
                for t in timeline_cols:
                    if start < t <= start + dur:
                        table.at[idx, t] = res
            except Exception:
                # Skip problematic rows rather than failing entirely
                continue
    
    def show_fallback_display(self):
        """Show basic information when RCPS analysis fails"""
        # Clear previous content
        for widget in self.tables_frame.winfo_children():
            widget.destroy()
        
        # Show simple message
        fallback_frame = ttk.Frame(self.tables_frame)
        fallback_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(fallback_frame, 
                 text="RCPS Analysis Unavailable", 
                 font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        ttk.Label(fallback_frame,
                 text="Please ensure your project data is valid and try again.\\n"
                      "If problems persist, try running CPM or PERT analysis first.",
                 justify=tk.CENTER).pack()
        
        # Add retry button
        ttk.Button(fallback_frame, 
                  text="Retry RCPS Analysis",
                  command=self.run_rcps_with_error_handling).pack(pady=(20, 0))
'''
        return enhanced_method
    
    def enhance_file(self):
        """Add error handling enhancements to the RCPS file"""
        print("🛡️ Adding Error Handling to RCPS Tab")
        print("=" * 40)
        
        if not self.rcps_file.exists():
            print(f"❌ RCPS file not found: {self.rcps_file}")
            return False
        
        # Read current file
        with open(self.rcps_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Add imports if not present
        if 'import logging' not in content:
            content = content.replace('import tkinter as tk', 'import tkinter as tk\nimport logging')
        
        # Add new methods before the last method or class end
        validation_method = self.add_input_validation()
        progress_method = self.add_progress_dialog()
        enhanced_run_method = self.add_enhanced_run_rcps()
        
        # Find insertion point (before the last method)
        insertion_point = content.rfind('    def display_gantt_chart')
        if insertion_point == -1:
            insertion_point = content.rfind('class RCPSTab:')
            if insertion_point != -1:
                # Find end of __init__ method
                insertion_point = content.find('def create_tab(self):', insertion_point)
        
        if insertion_point != -1:
            new_content = (content[:insertion_point] + 
                          validation_method + 
                          progress_method + 
                          enhanced_run_method + 
                          content[insertion_point:])
            
            # Update the run_rcps button command
            new_content = new_content.replace(
                'command=self.run_rcps',
                'command=self.run_rcps_with_error_handling'
            )
            
            # Write enhanced file
            with open(self.rcps_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✓ Error handling methods added")
            print("✓ Run button updated to use enhanced method")
            return True
        else:
            print("❌ Could not find insertion point in file")
            return False

def main():
    project_root = Path.cwd()
    enhancer = RCPSErrorHandlingEnhancer(project_root)
    
    if enhancer.enhance_file():
        print("\n🎉 Error handling enhancement completed!")
        print("\n📋 Added features:")
        print("- Comprehensive input validation")
        print("- Progress dialog for long operations")
        print("- Graceful error recovery")
        print("- User-friendly error messages")
        print("- Fallback display on failures")
        return 0
    else:
        print("\n❌ Enhancement failed")
        return 1

if __name__ == '__main__':
    exit(main())
