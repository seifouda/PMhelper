#!/usr/bin/env python3
"""
Clean up preproduction branch by removing non-essential files
"""

import os
import shutil
from pathlib import Path
import subprocess

def get_files_to_remove():
    """Get list of files and directories to remove from preproduction"""
    
    # Files to remove (non-essential for running the app)
    files_to_remove = [
        # Debug and analysis scripts
        "analyze_rcps_crashing_issue.py",
        "analyze_rcps_integration_options.py", 
        "check_rcps_table_structure.py",
        "compare_crashing_approaches.py",
        "compare_crashing_data.py",
        "compare_tabs.py",
        "debug_cost_data.py",
        "debug_gantt_button.py",
        "debug_missing_activities.py",
        "debug_normal_crashing.py",
        "debug_rcps_access_methods.py",
        "debug_rcps_data_flow.py",
        "debug_rcps_durations.py",
        "debug_rcps_enhancements.py",
        "debug_rcps_table_access.py",
        "debug_resource_calculation.py",
        "debug_toolbar.py",
        "demo_fullscreen_comparison.py",
        "execute_rcps_immediate_actions.py",
        "extract_network_attributes.py",
        "final_verification.py",
        "fix_rcps_crashing_bug.py",
        "fix_rcps_method_calls.py",
        "foundation_methods.py",
        "implement_rcps_table_integration.py",
        "integrate_phase1_methods.py",
        "investigate_rcps_issue.py",
        "minimal_toolbar_test.py",
        "quick_crashing_test.py",
        "quick_debug_rcps_crashing.py",
        "quick_start_phase1.py",
        "quick_test.py",
        "rcps_crashing_bypass_solution.py",
        "rcps_fix_summary.py",
        "rcps_issue_analysis.py",
        "simple_duration_analysis.py",
        "simple_ef_test.py",
        "simple_export_test.py",
        "simple_method_test.py",
        "validate_fullscreen_feature.py",
        "validate_overlaid_resource.py",
        "validate_rcps_fix.py",
        "validate_toolbar_fix.py",
        "validation_summary.py",
        "verify_export_fix.py",
        "verify_phase1_integration.py",
        "identify_essential_files.py",  # Our analysis script
        
        # Test files
        "test_actual_start_export_fix.py",
        "test_analyzer_access_final.py",
        "test_column_widths.py",
        "test_cost_flow.py",
        "test_cost_format.py",
        "test_crashing_analyzer_fix.py",
        "test_crashing_duration.py",
        "test_crashing_logic.py",
        "test_crashing_validation.py",
        "test_crashing_validation_sim.py",
        "test_direct_method.py",
        "test_duration_calculation.py",
        "test_ef_attributes_direct.py",
        "test_ef_attributes_final.py",
        "test_ef_duration_logic.py",
        "test_ef_verification.py",
        "test_enhanced_challenging.py",
        "test_enhanced_chart.py",
        "test_enhanced_costs.py",
        "test_enhanced_strategy.py",
        "test_fullscreen_comparison.py",
        "test_fullscreen_embedded.py",
        "test_fullscreen_feature.py",
        "test_fullscreen_fix.py",
        "test_phase1_foundation_methods.py",
        "test_phase3_intelligent_optimization.py",
        "test_prepare_crashing_dataframe.py",
        "test_rcps_actual_start_fix.py",
        "test_rcps_actual_start_fix_new.py",
        "test_rcps_bypass_instructions.py",
        "test_rcps_complete.py",
        "test_rcps_cost_tracking.py",
        "test_rcps_crashing_bug.py",
        "test_rcps_crashing_data_fix.py",
        "test_rcps_crashing_debugging.py",
        "test_rcps_crashing_direct.py",
        "test_rcps_crashing_fix_validation.py",
        "test_rcps_crashing_integration.py",
        "test_rcps_crashing_simple.py",
        "test_rcps_data_creation.py",
        "test_rcps_debug.py",
        "test_rcps_debug_output_fix.py",
        "test_rcps_duration_fix.py",
        "test_rcps_error_fix_validation.py",
        "test_rcps_fix.py",
        "test_rcps_fix_simple.py",
        "test_rcps_fullscreen_integration.py",
        "test_rcps_graph_direct.py",
        "test_rcps_graph_fixed.py",
        "test_rcps_hybrid.py",
        "test_rcps_methods_simple.py",
        "test_rcps_network_graph_fix.py",
        "test_rcps_network_simple.py",
        "test_rcps_network_simple_new.py",
        "test_rcps_recalculated_scheduling.py",
        "test_rcps_table_access.py",
        "test_rcps_table_integration.py",
        "test_rcps_workflow.py",
        "test_realistic_target.py",
        "test_simple_rcps_fix.py",
        "test_table_sizing.py",
        "test_toolbar_fix.py",
        "test_toolbar_functionality.py",
        "test_updated_layout.py",
        "test_with_selection.py"
    ]
    
    # Directories to remove
    dirs_to_remove = [
        "build",
        "dist", 
        "htmlcov",
        ".pytest_cache",
        ".venv",
        "tests",
        "code",
        "extensions",
        "templates",
        "scripts",
        "New folder"
    ]
    
    # Markdown files to remove (keeping only README.md)
    md_files_to_remove = []
    for md_file in Path(".").glob("*.md"):
        if md_file.name != "README.md":
            md_files_to_remove.append(str(md_file))
    
    # Log files to remove
    log_files = list(Path(".").glob("*.txt")) + list(Path(".").glob("*.log"))
    log_files_to_remove = [str(f) for f in log_files]
    
    return files_to_remove + md_files_to_remove + log_files_to_remove, dirs_to_remove

def clean_preproduction_branch():
    """Remove non-essential files from the preproduction branch"""
    
    files_to_remove, dirs_to_remove = get_files_to_remove()
    
    print("🧹 CLEANING PREPRODUCTION BRANCH")
    print("=" * 50)
    
    # Remove files
    removed_files = 0
    for file_path in files_to_remove:
        if Path(file_path).exists():
            try:
                os.remove(file_path)
                print(f"✓ Removed file: {file_path}")
                removed_files += 1
            except Exception as e:
                print(f"✗ Failed to remove {file_path}: {e}")
    
    # Remove directories
    removed_dirs = 0
    for dir_path in dirs_to_remove:
        if Path(dir_path).exists():
            try:
                shutil.rmtree(dir_path)
                print(f"✓ Removed directory: {dir_path}/")
                removed_dirs += 1
            except Exception as e:
                print(f"✗ Failed to remove {dir_path}/: {e}")
    
    # Remove __pycache__ directories recursively
    pycache_dirs = list(Path(".").rglob("__pycache__"))
    for pycache in pycache_dirs:
        try:
            shutil.rmtree(pycache)
            print(f"✓ Removed cache: {pycache}")
            removed_dirs += 1
        except Exception as e:
            print(f"✗ Failed to remove {pycache}: {e}")
    
    # Remove .pyc files
    pyc_files = list(Path(".").rglob("*.pyc"))
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"✓ Removed compiled: {pyc_file}")
            removed_files += 1
        except Exception as e:
            print(f"✗ Failed to remove {pyc_file}: {e}")
            
    # Remove .coverage file
    if Path(".coverage").exists():
        try:
            os.remove(".coverage")
            print("✓ Removed .coverage")
            removed_files += 1
        except Exception as e:
            print(f"✗ Failed to remove .coverage: {e}")
    
    print("\n" + "=" * 50)
    print(f"🎉 CLEANUP COMPLETE!")
    print(f"   Files removed: {removed_files}")
    print(f"   Directories removed: {removed_dirs}")
    
    # Show remaining essential files
    print("\n📁 REMAINING ESSENTIAL FILES:")
    essential_files = [
        "launch_app.py",
        "README.md", 
        ".gitignore",
        "src/",
        "config/",
        "assets/",
        "docs/"
    ]
    
    for item in essential_files:
        if Path(item).exists():
            if Path(item).is_dir():
                file_count = len(list(Path(item).rglob("*")))
                print(f"   ✓ {item} ({file_count} files)")
            else:
                print(f"   ✓ {item}")
        else:
            print(f"   ✗ {item} (missing)")
    
    return removed_files, removed_dirs

if __name__ == "__main__":
    removed_files, removed_dirs = clean_preproduction_branch()
